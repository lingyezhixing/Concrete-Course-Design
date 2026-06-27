"""板配筋计算工具

钢筋混凝土基本公式（h₀/αs/ξ/As）与连续梁系数表见 :mod:`app.solvers.common`。
本模块仅保留板专有的配筋逻辑——板按「钢筋直径 + 间距」配筋，与梁的
「根数 + 直径」配筋方式不同。
"""
from __future__ import annotations

from app.models.slab import ReinforcementBar, SectionReinforcement
from app.solvers.common import (
    alpha_s,
    as_required,
    effective_depth,
    flexure_status,
    xi,
)

__all__ = [
    "generate_rebar_candidates",
    "calc_section_reinforcement",
]

# 板常用钢筋直径 (mm) 与间距 (mm)
_STANDARD_DIAMETERS: list[int] = [6, 8, 10, 12, 14]
_STANDARD_SPACINGS: list[int] = [200, 180, 150, 120, 100, 80]


def generate_rebar_candidates(
    as_required: float,
    min_diameter: int = 8,
) -> list[ReinforcementBar]:
    """生成满足 As ≥ as_required 的板配筋方案（按面积升序）。

    板按「直径 + 间距」配筋：每米板宽面积 = π·d²/4 × (1000/s)。
    """
    candidates: list[ReinforcementBar] = []
    seen: set[str] = set()

    for d in _STANDARD_DIAMETERS:
        if d < min_diameter:
            continue
        for s in _STANDARD_SPACINGS:
            bar = ReinforcementBar(diameter=d, spacing=s)
            key = bar.display
            if key in seen:
                continue
            seen.add(key)
            if bar.area_per_meter >= as_required:
                candidates.append(bar)

    candidates.sort(key=lambda c: c.area_per_meter)
    return candidates


def calc_section_reinforcement(
    name: str,
    moment: float,
    h: float,
    cover: float,
    bar_diameter: float,
    fc: float,
    fy: float,
    gamma_d: float,
    b: float = 1000.0,
    min_bar_diameter: int = 8,
) -> SectionReinforcement:
    """计算单个板截面的配筋。

    h₀ = h − c − d/2
    αs = γd·M/(fc·b·h₀²)，ξ = 1 − √(1 − 2αs)，As = ξ·fc/fy·b·h₀
    """
    m = abs(moment)
    h0 = effective_depth(h, cover, bar_diameter)
    a_s = alpha_s(m, fc, b, h0, gamma_d)
    rel_xi = xi(a_s)
    as_req = as_required(rel_xi, fc, fy, b, h0)

    candidates = generate_rebar_candidates(as_req, min_diameter=min_bar_diameter)
    selected = candidates[0] if candidates else None
    as_prov = selected.area_per_meter if selected else 0.0

    return SectionReinforcement(
        name=name,
        moment=round(m, 4),
        h0=round(h0, 2),
        alpha_s=round(a_s, 4),
        xi=round(rel_xi, 4),
        as_required=round(as_req, 4),
        selected_bar=selected,
        as_provided=round(as_prov, 4),
        status=flexure_status(as_req, as_prov),
        candidates=candidates,
    )
