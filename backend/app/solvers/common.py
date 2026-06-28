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

from app.models.beam import BeamBarBundle, ShearDesignResult

__all__ = [
    "effective_depth",
    "alpha_s",
    "xi",
    "as_required",
    "flexure_status",
    "ContinuousBeamCoefficients",
    "get_continuous_beam_coefficients",
    "generate_bar_bundles",
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
# 梁配筋候选方案
# ──────────────────────────────────────────────

_STANDARD_BAR_DIAMETERS = [12, 14, 16, 18, 20, 22, 25]
_BAR_COUNTS = [2, 3, 4, 5, 6]
# 每层可放最大根数（按梁宽，保守取值）
_MAX_BARS_PER_LAYER = {200: 3, 250: 3, 300: 4, 350: 5}


def generate_bar_bundles(
    as_required: float,
    beam_width: int = 200,
    min_diameter: int = 12,
) -> list[BeamBarBundle]:
    """生成梁配筋候选方案（按面积升序）。

    Args:
        as_required: 所需钢筋面积 (mm²)
        beam_width: 梁宽 (mm)
        min_diameter: 最小钢筋直径 (mm)

    Returns:
        满足 As ≥ as_required 的候选方案，按面积升序
    """
    max_per_layer = _MAX_BARS_PER_LAYER.get(beam_width, 3)
    candidates: list[BeamBarBundle] = []
    seen: set[str] = set()

    for d in _STANDARD_BAR_DIAMETERS:
        if d < min_diameter:
            continue
        max_bars = min(6, max_per_layer * 2)  # 最多 2 层
        for n in _BAR_COUNTS:
            if n > max_bars:
                continue
            bar = BeamBarBundle(count=n, diameter=d)
            key = bar.display
            if key in seen:
                continue
            seen.add(key)
            if bar.area >= as_required:
                candidates.append(bar)

    candidates.sort(key=lambda c: c.area)
    return candidates


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
) -> ShearDesignResult:
    """计算梁斜截面箍筋（次梁、主梁共用）。

    公式（GB 50010-2010 式 6.3.4-2）：
      Vc = 0.7 · ft · b · h₀                          混凝土受剪（N）
      Asv/s = (γd · V − 0.7 · ft · b · h₀) / (fyv · h₀)    箍筋计算
      ρsv = Asv / (b × s)

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
    """
    v = abs(max_shear)
    h0 = effective_depth(h, cover, bar_diameter)

    vc = 0.7 * ft * b * h0 / gamma_d / 1000.0  # kN
    need_stirrups = v > vc

    asv = stirrup_legs * math.pi * stirrup_diameter**2 / 4.0

    if need_stirrups:
        # Asv/s = (γd·V − 0.7·ft·b·h₀) / (fyv·h₀)   (GB 50010-2010 式 6.3.4-2)
        asv_s = (gamma_d * v * 1e3 - 0.7 * ft * b * h0) / (fyv * h0)
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
