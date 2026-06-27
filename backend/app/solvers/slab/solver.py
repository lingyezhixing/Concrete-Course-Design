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
)
from app.solvers.slab.utils import get_slab_coefficients

__all__ = [
    "calculate_load",
    "calculate_spans",
    "calculate_net_spans",
    "convert_loads",
    "calculate_internal_forces",
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
    middle_span = inp.length / inp.spans
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
    span_unit = inp.length / inp.spans

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

    最终乘以结构系数。
    """
    g = converted.converted_dead
    q = converted.converted_live
    coeffs = get_slab_coefficients(inp.spans)
    n = inp.spans
    gamma = inp.structure_factor

    # ---- 弯矩 ----
    moments: list[SlabMomentResult] = []
    for i, (alpha, alpha1) in enumerate(zip(coeffs.moments, coeffs.moment_alpha1)):
        # 偶数索引是跨中，奇数索引是支座
        if i % 2 == 0:
            # 跨中 → 对应跨的序号为 i // 2
            span_idx = i // 2
            name = f"M{span_idx + 1}"
        else:
            # 支座 → 序号为 (i - 1) // 2，字母从 B 开始
            support_idx = (i - 1) // 2
            name = f"M_{chr(ord('A') + support_idx + 1)}"

        span_idx_for_l0 = i // 2
        st = _span_type_for_index(span_idx_for_l0, n)
        l0 = spans.edge_span if st == "edge" else spans.middle_span

        value = gamma * (alpha * g * l0 ** 2 + alpha1 * q * l0 ** 2)
        moments.append(SlabMomentResult(name=name, value=round(value, 4)))

    # ---- 剪力 ----
    shears: list[SlabShearResult] = []
    for i, (beta, beta1) in enumerate(zip(coeffs.shears, coeffs.shear_beta1)):
        # 剪力索引 i 对应的跨：i // 2
        span_idx = i // 2
        st = _span_type_for_index(span_idx, n)
        ln = net_spans.edge_net if st == "edge" else net_spans.middle_net

        # 命名
        if i == 0:
            name = "V_A"
        elif i == 2 * n - 1:
            name = f"V_{chr(ord('A') + n)}"
        elif i % 2 == 1:
            # 奇数 → 支座左侧，support_idx = i // 2
            support_idx = i // 2
            letter = chr(ord('A') + support_idx + 1)
            name = f"Vl_{letter}"
        else:
            # 偶数 → 支座右侧，support_idx = i // 2 - 1
            support_idx = i // 2 - 1
            letter = chr(ord('A') + support_idx + 1)
            name = f"Vr_{letter}"

        value = gamma * (beta * g * ln + beta1 * q * ln)
        shears.append(SlabShearResult(name=name, value=round(value, 4)))

    return SlabInternalForceOutput(moments=moments, shears=shears)
