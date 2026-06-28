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
from app.solvers.common import calc_continuous_beam_internal_forces
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

    支座边缘弯矩调整：M' = M + (b/2)·V₀，V₀ = (g'+q')·l₀/2（简支支座剪力）。
    内力计算主体（含 >5 跨简化）共用
    :func:`app.solvers.common.calc_continuous_beam_internal_forces`。
    """
    g = converted.converted_dead
    q = converted.converted_live

    # 支座边缘调整量：每个支座弯矩叠加 (b/2)·V₀
    b_support_m = inp.support_width / 1000.0
    support_delta = (b_support_m / 2.0) * (g + q) * spans.middle_span / 2.0

    moments_raw, shears_raw = calc_continuous_beam_internal_forces(
        g=g, q=q, n=inp.spans,
        middle_span=spans.middle_span, edge_span=spans.edge_span,
        middle_net=net_spans.middle_net, edge_net=net_spans.edge_net,
        support_moment_delta=support_delta,
    )
    moments = [BeamMomentResult(name=name, value=v) for name, v in moments_raw]
    shears = [BeamShearResult(name=name, value=v) for name, v in shears_raw]
    return BeamInternalForceOutput(moments=moments, shears=shears)


def calculate_beam(
    inp: BeamInput,
    fc: float,
    fy: float,
    gamma_d: float,
    ft: float = 1.10,
    cover: float = 30.0,
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
        ft=ft, fy=fy, gamma_d=gamma_d, stirrup_diameter=inp.stirrup_diameter,
    )

    return BeamFullResult(
        load=load, span=spans, net_span=net_spans, converted=converted,
        internal_forces=internal,
        reinforcement=BeamReinforcementOutput(flexure=flexure, shear=shear),
    )
