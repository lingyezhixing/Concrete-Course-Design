"""规范校核项：基于当前结果（含手改）实时判定。纯函数，供 /checks 端点调用。

系数与界限值沿用 SL 191-2008 / GB 50010，与已通过测试的求解器同源。
ft 为 C20 抗拉强度设计值 1.1（本课程用 C20）。
"""

from typing import Literal

from pydantic import BaseModel

from app.models.slab import SlabFullResult

# C20 抗拉强度设计值（N/mm²）；本课程固定 C20。
_FT_C20 = 1.1
# ≤C50: β1=0.8, εcu=0.0033, Es=2e5
_ES = 2e5
_EPS_CU = 0.0033
_BETA1 = 0.8


class CheckItem(BaseModel):
    name: str
    status: Literal["pass", "review", "fail"]
    clause: str
    detail: str


def _xi_b(fy: float) -> float:
    """相对界限受压区高度 ξb = β1 / (1 + fy/(Es·εcu))。"""
    return _BETA1 / (1.0 + fy / (_ES * _EPS_CU))


def _rho_min(fy: float) -> float:
    """最小配筋率 ρmin = max(0.2%, 45·ft/fy%)，C20 ft=1.1。"""
    return max(0.002, 0.45 * _FT_C20 / fy)


def check_slab(result: SlabFullResult, materials: dict) -> list[CheckItem]:
    """板的规范校核项（每截面 3 项：ξ、ρ、As）。"""
    fy = materials["fy_slab"]
    xi_b = _xi_b(fy)
    rho_min = _rho_min(fy)

    items: list[CheckItem] = []
    for s in result.reinforcement.sections:
        # 1) 相对受压区高度 ξ ≤ ξb
        xi_ok = s.xi <= xi_b
        items.append(CheckItem(
            name=f"{s.name} ξ ≤ ξb",
            status="pass" if xi_ok else "fail",
            clause="相对受压区高度上限",
            detail=f"ξ={s.xi:.4f}，ξb={xi_b:.4f}",
        ))

        # 2) 最小配筋率 ρ ≥ ρmin（板按 1m 板带 b=1000）
        rho = s.as_provided / (1000.0 * s.h0) if s.h0 > 0 else 0.0
        rho_ok = rho >= rho_min
        items.append(CheckItem(
            name=f"{s.name} ρ ≥ ρmin",
            status="pass" if rho_ok else "fail",
            clause="最小配筋率",
            detail=f"ρ={rho * 100:.3f}%，ρmin={rho_min * 100:.3f}%",
        ))

        # 3) 实配 ≥ 需要（复用求解器已判定的 status）
        status = {"推荐": "pass", "建议复核": "review", "不足": "fail"}.get(s.status, "fail")
        items.append(CheckItem(
            name=f"{s.name} As实 ≥ As需",
            status=status,
            clause="正截面配筋",
            detail=f"As需={s.as_required:.1f}，As实={s.as_provided:.1f}（{s.status}）",
        ))
    return items
