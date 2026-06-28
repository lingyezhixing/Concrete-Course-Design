"""板计算 — 荷载与跨度求解器"""

from app.models.slab import (
    SlabInput,
    SlabLoadOutput,
    SlabSpanOutput,
    SlabNetSpanOutput,
    SlabLoadConvertOutput,
    SlabMomentResult,
    SlabShearResult,
    SlabInternalForceOutput,
    SlabReinforcementOutput,
    SlabFullResult,
)
from app.solvers.common import get_continuous_beam_coefficients
from app.solvers.slab.utils import calc_section_reinforcement

__all__ = [
    "calculate_load",
    "calculate_spans",
    "calculate_net_spans",
    "convert_loads",
    "calculate_internal_forces",
    "calculate_slab_reinforcement",
    "calculate_slab",
]


def calculate_load(inp: SlabInput) -> SlabLoadOutput:
    """计算板荷载。

    恒载标准值 = 水磨石面层 + 板厚 × 混凝土重度 + 抹灰厚 × 抹灰重度
    恒载设计值 = 恒载分项系数 × 恒载标准值
    活荷载设计值 = 活载分项系数 × 活荷载标准值
    总荷载设计值 = (恒载设计值 + 活荷载设计值) × 1m 板带
    """
    # 恒载分项（kN/m²）
    terrazzo = inp.terrazzo_surface
    concrete = (inp.thickness / 1000.0) * inp.reinforced_concrete_weight
    plaster = (inp.plaster_thickness / 1000.0) * inp.plaster_weight

    # 恒载标准值与设计值
    dead_load_standard = terrazzo + concrete + plaster
    dead_load_design = inp.dead_load_factor * dead_load_standard

    # 活荷载
    live_load_standard = inp.live_load
    live_load_design = inp.live_load_factor * live_load_standard

    # 总荷载设计值（取 1 米板带，kN/m）
    total_load = (dead_load_design + live_load_design) * 1.0

    return SlabLoadOutput(
        terrazzo=round(terrazzo, 4),
        concrete=round(concrete, 4),
        plaster=round(plaster, 4),
        dead_load_standard=round(dead_load_standard, 4),
        dead_load_design=round(dead_load_design, 4),
        live_load_standard=round(live_load_standard, 4),
        live_load_design=round(live_load_design, 4),
        total_load=round(total_load, 4),
    )


def calculate_spans(inp: SlabInput) -> SlabSpanOutput:
    """计算板的计算跨度。

    中间跨: l0 = L / n
    边跨:   l0 = L / n - 0.120 + h / 2
    其中 0.120m 为规范固定值，h 为板厚（mm → m）
    """
    middle_span = inp.width / inp.spans
    edge_span = middle_span - 0.120 + inp.thickness / 2000.0

    return SlabSpanOutput(
        middle_span=round(middle_span, 4),
        edge_span=round(edge_span, 4),
    )


def calculate_net_spans(inp: SlabInput) -> SlabNetSpanOutput:
    """计算板的净跨度。

    中间跨: ln = L/n - b
    边跨:   ln = L/n - 0.120 - b/2
    其中 b 为支座宽度（mm → m），0.120m 为规范固定值
    """
    b = inp.support_width / 1000.0
    span_unit = inp.width / inp.spans

    middle_net = span_unit - b
    edge_net = span_unit - 0.120 - b / 2.0

    return SlabNetSpanOutput(
        middle_net=round(middle_net, 4),
        edge_net=round(edge_net, 4),
    )


def convert_loads(load: SlabLoadOutput) -> SlabLoadConvertOutput:
    """荷载折算。

    折算恒荷载 g = qG + qQ / 2
    折算活荷载 q = qQ / 2
    """
    converted_dead = load.dead_load_design + load.live_load_design / 2.0
    converted_live = load.live_load_design / 2.0

    return SlabLoadConvertOutput(
        converted_dead=round(converted_dead, 4),
        converted_live=round(converted_live, 4),
    )


def _span_type_for_index(span_index: int, total_spans: int) -> str:
    """判断某跨是边跨还是中间跨。"""
    if total_spans <= 2:
        return "edge"
    if span_index == 0 or span_index == total_spans - 1:
        return "edge"
    return "middle"


def calculate_internal_forces(
    inp: SlabInput,
    load: SlabLoadOutput,
    spans: SlabSpanOutput,
    net_spans: SlabNetSpanOutput,
    converted: SlabLoadConvertOutput,
) -> SlabInternalForceOutput:
    """综合求解器 — 计算各位置弯矩与剪力。

    M = α·g·l0² + α1·q·l0²   (弯矩，用计算跨度 l0)
    V = β·g·ln + β1·q·ln     (剪力，用净跨度 ln)

    系数查表仅支持 2 ~ 5 跨。当实际跨数 > 5 时，按 5 跨查表，
    保留左边两跨和右边两跨的系数，中间所有跨使用相同的中间跨系数。
    """
    g = converted.converted_dead
    q = converted.converted_live
    n = inp.spans
    effective_spans = min(n, 5)
    coeffs = get_continuous_beam_coefficients(effective_spans)

    def _map_span_table(actual_idx: int) -> int:
        if n <= 5:
            return actual_idx * 2
        if actual_idx == 0:
            return 0
        if actual_idx == 1:
            return 2
        if actual_idx == n - 2:
            return 6
        if actual_idx == n - 1:
            return 8
        return 4

    def _map_support_table(actual_idx: int) -> int:
        if n <= 5:
            return actual_idx * 2 + 1
        if actual_idx == 0:
            return 1
        if actual_idx == 1:
            return 3
        if actual_idx == n - 2:
            return 7
        return 5

    # ---- 弯矩 ----
    moments: list[SlabMomentResult] = []
    for pos in range(2 * n - 1):
        if pos % 2 == 0:
            span_idx = pos // 2
            ti = _map_span_table(span_idx)
            alpha = coeffs.moments[ti]
            alpha1 = coeffs.moment_alpha1[ti]
            st = _span_type_for_index(span_idx, n)
            l0 = spans.edge_span if st == "edge" else spans.middle_span
            value = alpha * g * l0 ** 2 + alpha1 * q * l0 ** 2
            moments.append(SlabMomentResult(name=f"M{span_idx + 1}", value=round(value, 4)))
        else:
            support_idx = (pos - 1) // 2
            ti = _map_support_table(support_idx)
            alpha = coeffs.moments[ti]
            alpha1 = coeffs.moment_alpha1[ti]
            l0 = spans.middle_span
            value = alpha * g * l0 ** 2 + alpha1 * q * l0 ** 2
            letter = chr(ord('A') + support_idx + 1)
            moments.append(SlabMomentResult(name=f"M_{letter}", value=round(value, 4)))

    # ---- 剪力 ----
    shears: list[SlabShearResult] = []
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
            letter = chr(ord('A') + support_idx + 1)
            name = f"Vl_{letter}"
        else:
            support_idx = pos // 2 - 1
            ti = _map_support_table(support_idx) + 1
            letter = chr(ord('A') + support_idx + 1)
            name = f"Vr_{letter}"

        if pos == 0 or pos == 2 * n - 1:
            ln = net_spans.edge_net
        else:
            ln = net_spans.middle_net
        beta = coeffs.shears[ti]
        beta1 = coeffs.shear_beta1[ti]
        value = beta * g * ln + beta1 * q * ln
        shears.append(SlabShearResult(name=name, value=round(value, 4)))

    return SlabInternalForceOutput(moments=moments, shears=shears)


def calculate_slab_reinforcement(
    moments: list[tuple[str, float]],
    h: float,
    cover: float,
    bar_diameter: float,
    fc: float,
    fy: float,
    gamma_d: float,
    b: float = 1000.0,
    min_bar_diameter: int = 8,
) -> SlabReinforcementOutput:
    """计算板全部截面的配筋。

    对每个 (截面名, 弯矩) 对依次进行正截面配筋计算，
    输出 αs、ξ、As_required、候选方案和推荐配筋。

    Args:
        moments: 截面弯矩列表 [(name, M), ...]
        h: 板厚 (mm)
        cover: 保护层厚度 (mm)
        bar_diameter: 钢筋估计直径 (mm)
        fc: 混凝土抗压强度设计值 (N/mm²)
        fy: 钢筋抗拉强度设计值 (N/mm²)
        gamma_d: 结构系数
        b: 截面宽度 (mm)，板取 1000
        min_bar_diameter: 最小钢筋直径 (mm)，板主筋通常 ≥ 8

    Returns:
        SlabReinforcementOutput
    """
    sections = []
    for name, moment in moments:
        sec = calc_section_reinforcement(
            name=name,
            moment=moment,
            h=h,
            cover=cover,
            bar_diameter=bar_diameter,
            fc=fc,
            fy=fy,
            gamma_d=gamma_d,
            b=b,
            min_bar_diameter=min_bar_diameter,
        )
        sections.append(sec)
    return SlabReinforcementOutput(sections=sections)


def calculate_slab(
    inp: SlabInput,
    fc: float,
    fy: float,
    gamma_d: float,
    cover: float = 20.0,
    bar_diameter: float = 10.0,
) -> SlabFullResult:
    """板完整计算编排：荷载 → 跨度 → 净跨 → 折算 → 内力 → 配筋。

    不改各步骤核心逻辑，仅做串联 + 供应构造默认值（cover / bar_diameter）。
    板按 1m 板带 (b=1000)、最小直径 8 配筋。
    """
    load = calculate_load(inp)
    spans = calculate_spans(inp)
    net_spans = calculate_net_spans(inp)
    converted = convert_loads(load)
    internal = calculate_internal_forces(inp, load, spans, net_spans, converted)

    moments = [(m.name, m.value) for m in internal.moments]
    reinforcement = calculate_slab_reinforcement(
        moments=moments,
        h=inp.thickness,
        cover=cover,
        bar_diameter=bar_diameter,
        fc=fc,
        fy=fy,
        gamma_d=gamma_d,
    )
    return SlabFullResult(
        load=load,
        span=spans,
        net_span=net_spans,
        converted=converted,
        internal_forces=internal,
        reinforcement=reinforcement,
    )
