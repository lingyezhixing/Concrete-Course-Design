"""主梁 — 系数表 + 配筋工具

三等跨连续梁，三等分集中荷载（课设文档表14-4）
4 种荷载布置 → 最不利组合包络

系数：M = K₁·P·l, V = K₁·P  (P 为对应工况的集中力)

钢筋混凝土基本公式、配筋候选、斜截面计算见 :mod:`app.solvers.common`。
"""
from __future__ import annotations

from app.models.beam import BeamFlexureResult, ShearDesignResult
from app.solvers.common import (
    alpha_s,
    as_required,
    calc_shear_design,
    effective_depth,
    flexure_status,
    generate_bar_bundles,
    xi,
)

__all__ = [
    "get_main_beam_coefficients",
    "calc_envelope",
    "calc_main_beam_flexure",
    "calc_main_beam_shear",
]


# ============================================================
# 系数表：三等跨连续梁，三等分集中荷载
# 列：G_all (G布满) | Q_13 (Q在1,3跨) | Q_2 (Q在第2跨) | Q_12 (Q在1,2跨)
# ============================================================

_MAIN_BEAM_COEFFICIENTS: dict[str, dict[str, float]] = {
    "M1":  {"G_all": 0.244, "Q_13": 0.289, "Q_2": -0.044, "Q_12": 0.229},
    "M2":  {"G_all": 0.067, "Q_13": -0.133, "Q_2": 0.200, "Q_12": 0.170},
    "M_B": {"G_all": -0.267, "Q_13": -0.133, "Q_2": -0.133, "Q_12": -0.311},
    "M_C": {"G_all": -0.267, "Q_13": -0.133, "Q_2": -0.133, "Q_12": -0.089},
    "VA":  {"G_all": 0.733, "Q_13": 0.866, "Q_2": -0.133, "Q_12": 0.689},
    "VBl": {"G_all": -1.267, "Q_13": -1.134, "Q_2": -0.133, "Q_12": -1.311},
    "VBr": {"G_all": 1.000, "Q_13": 0.000, "Q_2": 1.000, "Q_12": 1.222},
    "VCl": {"G_all": -1.000, "Q_13": 0.000, "Q_2": -1.000, "Q_12": -0.778},
    "VCr": {"G_all": 1.267, "Q_13": 1.134, "Q_2": 0.133, "Q_12": 0.089},
    "VD":  {"G_all": -0.733, "Q_13": -0.866, "Q_2": 0.133, "Q_12": 0.089},
}

# 最不利组合规则：(截面, G工况, Q工况)
_ENVELOPE_RULES = [
    ("M1", "G_all", "Q_13"),
    ("M2", "G_all", "Q_2"),
    ("M_B", "G_all", "Q_12"),
    ("M_C", "G_all", "Q_12"),
    ("VA", "G_all", "Q_13"),
    ("VBl", "G_all", "Q_12"),
    ("VBr", "G_all", "Q_12"),
]


def get_main_beam_coefficients() -> dict[str, dict[str, float]]:
    """获取主梁内力系数表"""
    return _MAIN_BEAM_COEFFICIENTS


def calc_envelope(G: float, Q: float, l0_edge: float, l0_interior: float) -> dict[str, float]:
    """计算最不利组合包络。

    弯矩：M = (K₁·G + K₂·Q) × l₀
      - 边跨跨中（M1）用边跨计算跨度 l0_edge（= 轴线跨）
      - 中跨跨中（M2）及支座（M_B, M_C）用中跨计算跨度
        l0_interior = 1.05 × (轴线 − 柱宽)
    剪力：V = K₁·G + K₂·Q（与跨度无关）
    """
    coeffs = get_main_beam_coefficients()
    result: dict[str, float] = {}
    edge_keys = {"M1"}

    for key, g_case, q_case in _ENVELOPE_RULES:
        k1 = coeffs[key][g_case]
        k2 = coeffs[key][q_case]
        if key.startswith("M"):
            l0 = l0_edge if key in edge_keys else l0_interior
            result[key] = (k1 * G + k2 * Q) * l0
        else:
            result[key] = k1 * G + k2 * Q

    return result


def calc_main_beam_flexure(
    name: str,
    moment: float,
    h: float,
    b: float,
    bf: float,
    hf: float,
    cover: float,
    bar_diameter: float,
    fc: float,
    fy: float,
    gamma_d: float,
    use_t_section: bool = True,
) -> BeamFlexureResult:
    """主梁正截面配筋（T 形截面，课程简化：支座也按 T 形）。"""
    m = abs(moment)
    h0 = effective_depth(h, cover, bar_diameter)

    if use_t_section:
        capacity = fc * bf * hf * (h0 - hf / 2.0) / gamma_d * 1e-6
        section_label = "T形(第一类)" if m <= capacity else "T形(第二类)"
        bw = bf
    else:
        section_label = "矩形"
        bw = b

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


def calc_main_beam_shear(
    max_shear: float,
    b: float,
    h: float,
    cover: float,
    bar_diameter: float,
    fc: float,
    gamma_d: float,
    stirrup_diameter: int = 10,
    stirrup_legs: int = 2,
    fyv: float = 270,
    hanger_force: float | None = None,
) -> ShearDesignResult:
    """主梁斜截面箍筋与吊筋（委托 :func:`app.solvers.common.calc_shear_design`）。"""
    return calc_shear_design(
        max_shear=max_shear,
        b=b, h=h, cover=cover, bar_diameter=bar_diameter,
        fc=fc, gamma_d=gamma_d,
        stirrup_diameter=stirrup_diameter,
        stirrup_legs=stirrup_legs,
        fyv=fyv,
        hanger_force=hanger_force,
    )
