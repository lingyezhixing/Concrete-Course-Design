"""次梁配筋计算工具

钢筋混凝土基本公式、配筋候选、斜截面计算见 :mod:`app.solvers.common`。
本模块保留次梁专有的正截面逻辑：跨中按 T 形截面、支座按矩形截面。
"""
from __future__ import annotations

from app.models.beam import BeamFlexureResult, ShearDesignResult
from app.solvers.common import (
    calc_flexure_design,
    calc_shear_design,
    effective_depth,
)

__all__ = [
    "calc_beam_flexure",
    "calc_beam_shear",
]


def calc_beam_flexure(
    name: str,
    moment: float,
    section_type: str,
    b: float,
    bf: float,
    h: float,
    hf: float,
    cover: float,
    bar_diameter: float,
    fc: float,
    fy: float,
    gamma_d: float,
) -> BeamFlexureResult:
    """计算次梁正截面配筋。

    T 形截面：跨中正弯矩，判断第一类（中和轴在翼缘内）→ 按 bf 宽矩形计算
    矩形截面：支座负弯矩，按 b 宽矩形计算

    Args:
        section_type: "T" 或 "rect"
        b: 梁宽 (mm)
        bf: 翼缘宽 (mm)，T 形时有效
        hf: 板厚 (mm)
    """
    m = abs(moment)
    h0 = effective_depth(h, cover, bar_diameter)

    if section_type.upper() == "T":
        # 第一类 T 形判定：M ≤ (1/γd) × fc × bf × hf × (h0 − hf/2)
        capacity = fc * bf * hf * (h0 - hf / 2.0) / gamma_d * 1e-6  # kN·m
        if m <= capacity:
            section_label, bw = "T形(第一类)", bf
        else:
            section_label, bw = "T形(第二类)", b  # 简化处理
    else:
        section_label, bw = "矩形", b

    return calc_flexure_design(name, moment, h0, b, bw, fc, fy, gamma_d, section_label)


def calc_beam_shear(
    max_shear: float,
    b: float,
    h: float,
    cover: float,
    bar_diameter: float,
    ft: float,
    fy: float,
    gamma_d: float,
    stirrup_diameter: int = 6,
    stirrup_legs: int = 2,
    fyv: float = 270,
) -> ShearDesignResult:
    """计算次梁斜截面箍筋（委托 :func:`app.solvers.common.calc_shear_design`）。"""
    return calc_shear_design(
        max_shear=max_shear,
        b=b, h=h, cover=cover, bar_diameter=bar_diameter,
        ft=ft, gamma_d=gamma_d,
        stirrup_diameter=stirrup_diameter,
        stirrup_legs=stirrup_legs,
        fyv=fyv,
    )
