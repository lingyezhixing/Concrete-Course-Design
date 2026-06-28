"""次梁计算 — 荷载、跨度、内力求解器

区别于板计算：
  1. 荷载组成不同（板传递 + 自重 + 粉刷）
  2. 折算荷载公式不同（g'+q/4, q'=3q/4）
  3. 跨度公式不同（梁的搁置/支撑规则）
  4. 内力系数表与板相同（等跨连续梁均布荷载）
"""

from app.models.beam import (
    BeamInput,
    BeamLoadOutput,
    BeamSpanOutput,
    BeamNetSpanOutput,
    BeamLoadConvertOutput,
    BeamMomentResult,
    BeamShearResult,
    BeamInternalForceOutput,
    BeamFullResult,
    BeamReinforcementOutput,
)
from app.solvers.common import get_continuous_beam_coefficients
from app.solvers.beam.utils import calc_beam_flexure, calc_beam_shear

__all__ = [
    "calculate_beam_load",
    "calculate_beam_spans",
    "calculate_beam_net_spans",
    "convert_beam_loads",
    "calculate_beam_internal_forces",
    "calculate_beam",
]


def calculate_beam_load(inp: BeamInput) -> BeamLoadOutput:
    """计算次梁荷载。

    荷载组成：
      板传来恒载 = 板恒载标准值 × 次梁间距
      次梁自重 = 混凝土重度 × 梁宽 × (梁高 - 板厚)
      次梁粉刷 = 抹灰重度 × 抹灰厚 × (梁高 - 板厚) × 2（两侧）
      恒载标准值 = 板传来 + 自重 + 粉刷
      恒载设计值 = 恒载分项系数 × 恒载标准值
      活载设计值 = 活载分项系数 × 活荷载标准值
    """
    dh = (inp.beam_height - inp.slab_thickness) / 1000.0  # 梁高-板厚 (m)

    # 恒载各分量
    from_slab_dead = inp.slab_dead_load_standard * inp.beam_spacing
    self_weight = inp.concrete_weight * (inp.beam_width / 1000.0) * dh
    plaster = inp.plaster_weight * (inp.plaster_thickness / 1000.0) * dh * 2

    dead_load_standard = from_slab_dead + self_weight + plaster
    dead_load_design = inp.dead_load_factor * dead_load_standard

    # 活荷载
    live_load_standard = inp.live_load_per_area * inp.beam_spacing
    live_load_design = inp.live_load_factor * live_load_standard

    return BeamLoadOutput(
        from_slab_dead=round(from_slab_dead, 4),
        self_weight=round(self_weight, 4),
        plaster=round(plaster, 4),
        dead_load_standard=round(dead_load_standard, 4),
        dead_load_design=round(dead_load_design, 4),
        live_load_standard=round(live_load_standard, 4),
        live_load_design=round(live_load_design, 4),
    )


def convert_beam_loads(load: BeamLoadOutput) -> BeamLoadConvertOutput:
    """次梁荷载折算。

    次梁公式：g' = g + q/4,  q' = 3q/4
    （区别于板的 g'=g+q/2, q'=q/2）
    """
    converted_dead = load.dead_load_design + load.live_load_design / 4.0
    converted_live = 3.0 * load.live_load_design / 4.0

    return BeamLoadConvertOutput(
        converted_dead=round(converted_dead, 4),
        converted_live=round(converted_live, 4),
    )


def calculate_beam_spans(inp: BeamInput) -> BeamSpanOutput:
    """计算次梁的弯矩计算跨度 l₀。

    边跨/中跨均按参考网站简化取轴线跨度 L（柱中到柱中）。
    规范公式做备查。
    """
    middle_span = inp.span
    edge_span = inp.span  # 参考网站简化取与中跨相同

    return BeamSpanOutput(
        middle_span=round(middle_span, 4),
        edge_span=round(edge_span, 4),
    )


def calculate_beam_net_spans(inp: BeamInput) -> BeamNetSpanOutput:
    """计算次梁的净跨度 lₙ（用于剪力计算）。

    边跨：ln = L - a/2 - b/2
          其中 a = 次梁搁置长度, b = 主梁宽
    中跨：ln = L - 主梁宽
    """
    b_support = inp.support_width / 1000.0
    a_bearing = inp.bearing_length / 1000.0

    edge_net = inp.span - a_bearing / 2.0 - b_support / 2.0
    middle_net = inp.span - b_support

    return BeamNetSpanOutput(
        middle_net=round(middle_net, 4),
        edge_net=round(edge_net, 4),
    )


def _span_type_for_index(span_index: int, total_spans: int) -> str:
    """判断某跨是边跨还是中间跨。"""
    if total_spans <= 2:
        return "edge"
    if span_index == 0 or span_index == total_spans - 1:
        return "edge"
    return "middle"


def calculate_beam_internal_forces(
    inp: BeamInput,
    load: BeamLoadOutput,
    spans: BeamSpanOutput,
    net_spans: BeamNetSpanOutput,
    converted: BeamLoadConvertOutput,
) -> BeamInternalForceOutput:
    """综合求解器 — 计算次梁各位置弯矩与剪力。

    M = α·g'·l₀² + α₁·q'·l₀²
    V = β·g'·lₙ + β₁·q'·lₙ

    支座弯矩做边缘调整：M' = |Mc| − b/2 × V₀
    V₀ = (g' + q') × l₀ / 2（简支梁支座剪力）

    系数复用 slab 的连续梁系数表（2~5 跨等跨连续梁均布荷载）。
    """
    g = converted.converted_dead
    q = converted.converted_live
    n = inp.spans
    effective_spans = min(n, 5)
    coeffs = get_continuous_beam_coefficients(effective_spans)

    # 支座边缘弯矩调整参数
    b_support_m = inp.support_width / 1000.0
    l0 = spans.middle_span
    v0_simple = (g + q) * l0 / 2.0

    def _map_span_table(actual_idx: int) -> int:
        if n <= 5:
            return actual_idx * 2
        if actual_idx == 0: return 0
        if actual_idx == 1: return 2
        if actual_idx == n - 2: return 6
        if actual_idx == n - 1: return 8
        return 4

    def _map_support_table(actual_idx: int) -> int:
        if n <= 5:
            return actual_idx * 2 + 1
        if actual_idx == 0: return 1
        if actual_idx == 1: return 3
        if actual_idx == n - 2: return 7
        return 5

    # ---- 弯矩 ----
    moments: list[BeamMomentResult] = []
    for pos in range(2 * n - 1):
        if pos % 2 == 0:
            span_idx = pos // 2
            ti = _map_span_table(span_idx)
            alpha = coeffs.moments[ti]
            alpha1 = coeffs.moment_alpha1[ti]
            st = _span_type_for_index(span_idx, n)
            l0 = spans.edge_span if st == "edge" else spans.middle_span
            value = alpha * g * l0 ** 2 + alpha1 * q * l0 ** 2
            moments.append(BeamMomentResult(name=f"M{span_idx + 1}", value=round(value, 4)))
        else:
            support_idx = (pos - 1) // 2
            ti = _map_support_table(support_idx)
            alpha = coeffs.moments[ti]
            alpha1 = coeffs.moment_alpha1[ti]
            l0 = spans.middle_span
            value = alpha * g * l0 ** 2 + alpha1 * q * l0 ** 2
            # 支座边缘弯矩调整：M' = M + (b/2) × V₀
            # 对负弯矩绝对值减小（往正方向移动）
            value = value + (b_support_m / 2.0) * v0_simple
            letter = chr(ord("A") + support_idx + 1)
            moments.append(BeamMomentResult(name=f"M_{letter}", value=round(value, 4)))

    # ---- 剪力 ----
    shears: list[BeamShearResult] = []
    for pos in range(2 * n):
        span_idx = pos // 2
        if pos == 0:
            ti = 0
            name = "V_A"
        elif pos == 2 * n - 1:
            ti = 2 * effective_spans - 1
            name = f"V_{chr(ord('A') + n)}"
        elif pos % 2 == 1:
            support_idx = pos // 2
            ti = _map_support_table(support_idx)
            letter = chr(ord("A") + support_idx + 1)
            name = f"Vl_{letter}"
        else:
            support_idx = pos // 2 - 1
            ti = _map_support_table(support_idx) + 1
            letter = chr(ord("A") + support_idx + 1)
            name = f"Vr_{letter}"

        if pos == 0 or pos == 2 * n - 1:
            ln = net_spans.edge_net
        else:
            ln = net_spans.middle_net
        beta = coeffs.shears[ti]
        beta1 = coeffs.shear_beta1[ti]
        value = beta * g * ln + beta1 * q * ln
        shears.append(BeamShearResult(name=name, value=round(value, 4)))

    return BeamInternalForceOutput(moments=moments, shears=shears)


def calculate_beam(
    inp: BeamInput,
    fc: float,
    fy: float,
    gamma_d: float,
    cover: float = 25.0,
    bar_diameter: float = 20.0,
) -> BeamFullResult:
    """次梁完整计算编排：荷载 → 跨度 → 净跨 → 折算 → 内力 → 配筋(正截面+斜截面)。

    不改各步骤核心逻辑，仅串联 + 供应构造默认值（cover/bar_diameter）。
    截面类型：跨中正弯矩 → T 形；支座负弯矩 → 矩形。
    翼缘 bf = 次梁间距 × 1000 (mm)；hf = 板厚。
    """
    load = calculate_beam_load(inp)
    spans = calculate_beam_spans(inp)
    net_spans = calculate_beam_net_spans(inp)
    converted = convert_beam_loads(load)
    internal = calculate_beam_internal_forces(inp, load, spans, net_spans, converted)

    b = inp.beam_width
    h = inp.beam_height
    bf = inp.beam_spacing * 1000.0
    hf = inp.slab_thickness

    flexure = []
    for m in internal.moments:
        section_type = "T" if m.value >= 0 else "rect"  # 正弯矩跨中T形，负弯矩支座矩形
        flexure.append(calc_beam_flexure(
            name=m.name, moment=m.value, section_type=section_type,
            b=b, bf=bf, h=h, hf=hf, cover=cover, bar_diameter=bar_diameter,
            fc=fc, fy=fy, gamma_d=gamma_d,
        ))

    max_shear = max((abs(s.value) for s in internal.shears), default=0.0)
    shear = calc_beam_shear(
        max_shear=max_shear, b=b, h=h, cover=cover, bar_diameter=bar_diameter,
        fc=fc, fy=fy, gamma_d=gamma_d,
    )

    return BeamFullResult(
        load=load, span=spans, net_span=net_spans, converted=converted,
        internal_forces=internal,
        reinforcement=BeamReinforcementOutput(flexure=flexure, shear=shear),
    )
