"""钢筋混凝土计算公共模块

收纳各求解器共用的基本公式与查表逻辑：
- 正截面配筋基本公式：有效高度 h₀、αs、ξ、As
- 配筋状态判定
- 等跨连续梁均布荷载系数表（板、次梁共用）
- 梁配筋候选方案生成（次梁、主梁共用）
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from app.models.beam import BeamBarBundle, BeamFlexureResult, ShearDesignResult

__all__ = [
    "effective_depth",
    "alpha_s",
    "xi",
    "as_required",
    "flexure_status",
    "ContinuousBeamCoefficients",
    "get_continuous_beam_coefficients",
    "calc_continuous_beam_internal_forces",
    "generate_bar_bundles",
    "calc_flexure_design",
    "calc_shear_design",
]


# ──────────────────────────────────────────────
# 正截面配筋基本公式
# ──────────────────────────────────────────────


def effective_depth(h: float, cover: float, bar_diameter: float) -> float:
    """有效高度 h₀ = h − c − d/2 (mm)"""
    return h - cover - bar_diameter / 2.0


def alpha_s(moment: float, fc: float, b: float, h0: float, gamma_d: float) -> float:
    """截面抵抗矩系数 αs = γd·M / (fc·b·h₀²)

    Args:
        moment: 弯矩设计值 (kN·m)
        fc: 混凝土抗压强度 (N/mm²)
        b: 截面宽度 (mm)
        h0: 有效高度 (mm)
        gamma_d: 结构系数
    """
    return gamma_d * moment * 1e6 / (fc * b * h0**2)


def xi(alpha_s: float) -> float:
    """相对受压区高度 ξ = 1 − √(1 − 2αs)"""
    return 1 - math.sqrt(1 - 2 * alpha_s)


def as_required(xi: float, fc: float, fy: float, b: float, h0: float) -> float:
    """所需钢筋面积 As = ξ·(fc/fy)·b·h₀ (mm²)"""
    return xi * (fc / fy) * b * h0


def flexure_status(as_req: float, as_prov: float) -> str:
    """根据需要面积与实配面积判定配筋状态。

    - 实配为 0 → "不足"
    - 实配 / 需要 > 1.8 → "建议复核"（超配过多，复核经济性）
    - 否则 → "推荐"
    """
    if as_prov == 0:
        return "不足"
    if as_prov / as_req > 1.8:
        return "建议复核"
    return "推荐"


# ──────────────────────────────────────────────
# 等跨连续梁系数表（板、次梁共用）
# 弯矩按：跨1中, 支座B, 跨2中, 支座C, ... 顺序
# 剪力按：端支座A, 支座B左, 支座B右, ... 顺序
# ──────────────────────────────────────────────


@dataclass
class ContinuousBeamCoefficients:
    """某跨数连续梁的完整系数集合"""

    spans: int
    moments: list[float]  # 弯矩系数
    shears: list[float]  # 剪力系数
    moment_alpha1: list[float]  # 活荷载弯矩系数
    shear_beta1: list[float]  # 活荷载剪力系数


_COEFFICIENTS: dict[int, ContinuousBeamCoefficients] = {
    2: ContinuousBeamCoefficients(
        spans=2,
        moments=[0.070, -0.125, 0.070],
        moment_alpha1=[0.096, -0.125, 0.096],
        shears=[0.375, -0.625, 0.625, -0.375],
        shear_beta1=[0.437, -0.625, 0.625, -0.437],
    ),
    3: ContinuousBeamCoefficients(
        spans=3,
        moments=[0.080, -0.100, 0.025, -0.100, 0.080],
        moment_alpha1=[0.101, -0.117, 0.075, -0.117, 0.101],
        shears=[0.400, -0.600, 0.500, -0.500, 0.600, -0.400],
        shear_beta1=[0.450, -0.617, 0.583, -0.583, 0.617, -0.450],
    ),
    4: ContinuousBeamCoefficients(
        spans=4,
        moments=[0.077, -0.107, 0.036, -0.071, 0.036, -0.107, 0.077],
        moment_alpha1=[0.100, -0.121, 0.081, -0.107, 0.081, -0.121, 0.100],
        shears=[0.393, -0.607, 0.536, -0.464, 0.464, -0.536, 0.607, -0.393],
        shear_beta1=[0.446, -0.620, 0.603, -0.571, 0.517, -0.603, 0.620, -0.446],
    ),
    5: ContinuousBeamCoefficients(
        spans=5,
        moments=[0.0781, -0.105, 0.0331, -0.079, 0.0462, -0.079, 0.0331, -0.105, 0.0781],
        moment_alpha1=[0.100, -0.119, 0.0787, -0.111, 0.0855, -0.111, 0.0787, -0.119, 0.100],
        shears=[0.394, -0.606, 0.526, -0.474, 0.500, -0.500, 0.474, -0.526, 0.606, -0.394],
        shear_beta1=[0.447, -0.620, 0.598, -0.576, 0.591, -0.591, 0.576, -0.598, 0.620, -0.447],
    ),
}


def get_continuous_beam_coefficients(spans: int) -> ContinuousBeamCoefficients:
    """根据跨数获取等跨连续梁（均布荷载）系数。

    Args:
        spans: 跨数，支持 2 ~ 5

    Raises:
        ValueError: 跨数不在支持范围内
    """
    if spans not in _COEFFICIENTS:
        raise ValueError(f"不支持 {spans} 跨，目前仅支持 2 ~ 5 跨")
    return _COEFFICIENTS[spans]


# ──────────────────────────────────────────────
# 等跨连续梁内力计算（板、次梁共用）
# ──────────────────────────────────────────────


def _span_type_for_index(span_index: int, total_spans: int) -> str:
    """判断某跨是边跨还是中间跨。"""
    if total_spans <= 2:
        return "edge"
    if span_index == 0 or span_index == total_spans - 1:
        return "edge"
    return "middle"


def _map_span_table(actual_idx: int, n: int) -> int:
    """实际跨序号 → 系数表索引。

    n ≤ 5 直接按位置取；n > 5 时按 5 跨简化：保留左右各两跨，
    其余中间跨共用同一中跨系数（索引 4）。
    """
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


def _map_support_table(actual_idx: int, n: int) -> int:
    """实际支座序号 → 系数表索引（n > 5 同样按 5 跨简化）。"""
    if n <= 5:
        return actual_idx * 2 + 1
    if actual_idx == 0:
        return 1
    if actual_idx == 1:
        return 3
    if actual_idx == n - 2:
        return 7
    return 5


def calc_continuous_beam_internal_forces(
    g: float,
    q: float,
    n: int,
    middle_span: float,
    edge_span: float,
    middle_net: float,
    edge_net: float,
    support_moment_delta: float = 0.0,
) -> tuple[list[tuple[str, float]], list[tuple[str, float]]]:
    """等跨连续梁（均布荷载）内力计算 — 板、次梁共用。

    M = α·g·l0² + α1·q·l0²   (弯矩，用计算跨度 l0)
    V = β·g·ln + β1·q·ln     (剪力，用净跨度 ln)

    系数查表仅支持 2~5 跨；n > 5 时按 5 跨查表（见 :func:`_map_span_table`）。
    支座弯矩统一叠加 ``support_moment_delta``（次梁做支座边缘调整 M+(b/2)·V₀；板为 0）。

    Returns:
        (moments, shears)：各为 ``(截面名, 设计值)`` 元组列表，值已 round 到 4 位。
    """
    effective_spans = min(n, 5)
    coeffs = get_continuous_beam_coefficients(effective_spans)

    # ---- 弯矩 ----
    moments: list[tuple[str, float]] = []
    for pos in range(2 * n - 1):
        if pos % 2 == 0:
            span_idx = pos // 2
            ti = _map_span_table(span_idx, n)
            alpha = coeffs.moments[ti]
            alpha1 = coeffs.moment_alpha1[ti]
            l0 = edge_span if _span_type_for_index(span_idx, n) == "edge" else middle_span
            value = alpha * g * l0 ** 2 + alpha1 * q * l0 ** 2
            moments.append((f"M{span_idx + 1}", round(value, 4)))
        else:
            support_idx = (pos - 1) // 2
            ti = _map_support_table(support_idx, n)
            alpha = coeffs.moments[ti]
            alpha1 = coeffs.moment_alpha1[ti]
            value = alpha * g * middle_span ** 2 + alpha1 * q * middle_span ** 2
            value += support_moment_delta
            letter = chr(ord("A") + support_idx + 1)
            moments.append((f"M_{letter}", round(value, 4)))

    # ---- 剪力 ----
    shears: list[tuple[str, float]] = []
    for pos in range(2 * n):
        if pos == 0:
            ti = 0
            name = "V_A"
        elif pos == 2 * n - 1:
            ti = 2 * effective_spans - 1
            name = f"V_{chr(ord('A') + n)}"
        elif pos % 2 == 1:
            support_idx = pos // 2
            ti = _map_support_table(support_idx, n)
            letter = chr(ord("A") + support_idx + 1)
            name = f"Vl_{letter}"
        else:
            support_idx = pos // 2 - 1
            ti = _map_support_table(support_idx, n) + 1
            letter = chr(ord("A") + support_idx + 1)
            name = f"Vr_{letter}"

        ln = edge_net if (pos == 0 or pos == 2 * n - 1) else middle_net
        beta = coeffs.shears[ti]
        beta1 = coeffs.shear_beta1[ti]
        value = beta * g * ln + beta1 * q * ln
        shears.append((name, round(value, 4)))

    return moments, shears


# ──────────────────────────────────────────────
# 梁配筋候选方案
# 依据《附表 3-1 钢筋的公称直径、公称截面积及理论质量》
# ──────────────────────────────────────────────

# 附表 3-1 梁纵向受力筋常用公称直径 (mm)
_STANDARD_BAR_DIAMETERS = [12, 14, 16, 18, 20, 22, 25, 28, 32]
# 附表 3-1 单根钢筋公称截面积 (mm²)
_SINGLE_BAR_AREA = {
    12: 113.1, 14: 153.9, 16: 201.1, 18: 254.5, 20: 314.2,
    22: 380.1, 25: 490.9, 28: 615.8, 32: 804.2,
}
# 候选根数范围（单层布置）
_BAR_COUNTS = [2, 3, 4, 5, 6, 7, 8]
# 梁下部纵向受力筋最小净距 (GB 50010)：≥ 25mm
_MIN_BAR_CLEARANCE = 25.0


def bar_clearance(beam_width: float, count: int, diameter: float) -> float:
    """梁宽方向钢筋净距 (b − n·d)/(n+1) (mm)。"""
    return (beam_width - count * diameter) / (count + 1)


def generate_bar_bundles(
    as_required: float,
    beam_width: int = 200,
) -> list[BeamBarBundle]:
    """生成梁配筋候选方案（按面积升序）。

    依据附表 3-1 的「直径 × 根数」组合，筛选同时满足以下两项的方案：

    1. ``As = n × 单根公称面积 ≥ as_required``
    2. 净距 ``(b − n·d)/(n+1) ≥ 25mm``（单层布置，GB 50010 下部筋最小净距）

    Args:
        as_required: 所需钢筋面积 (mm²)
        beam_width: 梁宽 (mm)

    Returns:
        满足要求的候选方案，按面积升序
    """
    candidates: list[BeamBarBundle] = []

    for d in _STANDARD_BAR_DIAMETERS:
        for n in _BAR_COUNTS:
            if bar_clearance(beam_width, n, d) < _MIN_BAR_CLEARANCE:
                continue
            bar = BeamBarBundle(count=n, diameter=d)
            if bar.area >= as_required:
                candidates.append(bar)

    candidates.sort(key=lambda c: c.area)
    return candidates


def calc_flexure_design(
    name: str,
    moment: float,
    h0: float,
    b: float,
    bw: float,
    fc: float,
    fy: float,
    gamma_d: float,
    section_label: str,
) -> BeamFlexureResult:
    """正截面受弯配筋的力学计算（次梁、主梁共用）。

    截面分类（T 形第一/二类 vs 矩形）及计算宽 ``bw`` 由调用方按构件规则决定后传入；
    本函数只负责 h₀→αs→ξ→As→选筋→状态→结果的统一流程。

    Args:
        moment: 弯矩设计值 (kN·m)，内部取绝对值
        h0: 有效高度 (mm)，由调用方算好（截面分类也需用到）
        b: 梁宽 (mm)，用于限制钢筋布置根数
        bw: 计算采用的截面宽 (mm)
        fc, fy: 材料强度设计值 (N/mm²)
        gamma_d: 结构系数
        section_label: 截面类型文案（如 "T形(第一类)" / "矩形"）
    """
    m = abs(moment)
    a_s = alpha_s(m, fc, bw, h0, gamma_d)
    rel_xi = xi(a_s)
    as_req = as_required(rel_xi, fc, fy, bw, h0)

    candidates = generate_bar_bundles(as_req, beam_width=int(b))
    selected = candidates[0] if candidates else None
    as_prov = selected.area if selected else 0.0

    return BeamFlexureResult(
        name=name,
        moment=round(m, 4),
        h0=round(h0, 2),
        section_type=section_label,
        width_used=round(bw, 2),
        alpha_s=round(a_s, 4),
        xi=round(rel_xi, 4),
        as_required=round(as_req, 4),
        selected_bar=selected,
        as_provided=round(as_prov, 4),
        status=flexure_status(as_req, as_prov),
        candidates=candidates,
    )


# ──────────────────────────────────────────────
# 梁斜截面箍筋
# ──────────────────────────────────────────────


def calc_shear_design(
    max_shear: float,
    b: float,
    h: float,
    cover: float,
    bar_diameter: float,
    ft: float,
    gamma_d: float,
    stirrup_diameter: int = 6,
    stirrup_legs: int = 2,
    fyv: float = 270,
    hanger_force: float | None = None,
    vc_coef: float = 0.7,
) -> ShearDesignResult:
    """计算梁斜截面箍筋（次梁、主梁共用）。

    公式（GB 50010-2010 式 6.3.4-2）：
      Vc = vc_coef · ft · b · h₀                       混凝土受剪（N）
      Asv/s = (γd · V − vc_coef · ft · b · h₀) / (fyv · h₀)  箍筋计算
      ρsv = Asv / (b × s)
    vc_coef：均布荷载为主的一般受剪构件取 0.7（默认）；
             集中荷载为主的梁（主梁）取 0.5。

    Args:
        max_shear: 最大剪力 (kN)
        b: 梁宽 (mm)
        h: 梁高 (mm)
        cover: 保护层 (mm)
        bar_diameter: 纵筋估计直径 (mm)
        ft: 混凝土抗拉强度 (N/mm²)
        gamma_d: 结构系数
        stirrup_diameter: 箍筋直径 (mm)
        stirrup_legs: 箍筋肢数
        fyv: 箍筋抗拉强度 (N/mm²)
        hanger_force: 吊筋计算集中力 (kN)，主梁使用
      vc_coef: 混凝土受剪系数（均布为主 0.7、集中荷载为主 0.5）
    """
    v = abs(max_shear)
    h0 = effective_depth(h, cover, bar_diameter)

    vc = vc_coef * ft * b * h0 / gamma_d / 1000.0  # kN
    need_stirrups = v > vc

    asv = stirrup_legs * math.pi * stirrup_diameter**2 / 4.0

    if need_stirrups:
        # Asv/s = (γd·V − vc_coef·ft·b·h₀) / (fyv·h₀)   (GB 50010-2010 式 6.3.4-2)
        asv_s = (gamma_d * v * 1e3 - vc_coef * ft * b * h0) / (fyv * h0)
        spacing = asv / asv_s if asv_s > 0 else 200
    else:
        asv_s = 0.0
        spacing = 200  # 构造配筋

    spacing = min(spacing, 200)  # 最大间距 200mm（规范构造要求）
    spacing = math.floor(spacing / 5) * 5  # 取整到 5mm
    stirrup_ratio = asv / (b * spacing) if spacing > 0 else 0

    # 吊筋 Asb = γd × F / (fyv × sin45°)
    if hanger_force and hanger_force > 0:
        hanger_area = gamma_d * hanger_force * 1e3 / (fyv * math.sin(math.pi / 4))
    else:
        hanger_area = 0.0

    return ShearDesignResult(
        max_shear=round(v, 4),
        h0=round(h0, 2),
        vc=round(vc, 4),
        need_stirrups=need_stirrups,
        asv_s=round(asv_s, 4),
        stirrup_diameter=stirrup_diameter,
        stirrup_legs=stirrup_legs,
        asv=round(asv, 4),
        recommended_spacing=round(spacing, 2),
        stirrup_ratio=round(stirrup_ratio, 4),
        hanger_area=round(hanger_area, 4),
    )
