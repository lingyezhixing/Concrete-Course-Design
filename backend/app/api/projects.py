"""项目生命周期路由：CRUD + （Task 8 追加）/calculate + /checks。

全部 Depends(get_current_user)，按 user_id 隔离；非自有资源 404。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.checks import check_slab
from app.data import project_repository as repo
from app.models.project import (
    CalculateRequest,
    MATERIALS_REQUIRED,
    ProjectCreate,
    ProjectPatch,
    ProjectPublic,
    SLAB_REQUIRED_INPUT,
)
from app.models.slab import SlabFullResult, SlabInput
from app.solvers.slab.solver import calculate_slab

router = APIRouter(prefix="/projects", tags=["projects"])


def _to_public(project: dict, has_uncommitted: bool) -> ProjectPublic:
    return ProjectPublic(
        id=project["id"],
        name=project["name"],
        data=project["data"],
        created_at=project["created_at"],
        updated_at=project["updated_at"],
        last_opened_at=project["last_opened_at"],
        has_uncommitted=has_uncommitted,
    )


def _has_uncommitted(user_id: int, project: dict) -> bool:
    """是否有「自上次提交点（创建或最新归档）之后的改动」。
    提交点 = 最新快照 created_at（若有），否则项目 created_at。
    has_uncommitted = updated_at > 提交点。
    """
    snaps = repo.list_snapshots(user_id, project["id"])
    commit_point = snaps[0]["created_at"] if snaps else project["created_at"]
    return project["updated_at"] > commit_point


@router.get("", response_model=list[ProjectPublic])
def list_projects(current_user: dict = Depends(get_current_user)):
    projects = repo.list_projects(current_user["id"])
    return [_to_public(p, _has_uncommitted(current_user["id"], p)) for p in projects]


@router.post("", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, current_user: dict = Depends(get_current_user)):
    project = repo.create_project(current_user["id"], payload.name)
    return _to_public(project, _has_uncommitted(current_user["id"], project))


@router.get("/{project_id}", response_model=ProjectPublic)
def get_project(project_id: int, current_user: dict = Depends(get_current_user)):
    repo.touch_opened(current_user["id"], project_id)
    project = repo.get_project(current_user["id"], project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return _to_public(project, _has_uncommitted(current_user["id"], project))


@router.patch("/{project_id}", response_model=ProjectPublic)
def update_project(
    project_id: int, payload: ProjectPatch, current_user: dict = Depends(get_current_user)
):
    project = repo.update_project(
        current_user["id"], project_id, data=payload.data, name=payload.name
    )
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")
    return _to_public(project, _has_uncommitted(current_user["id"], project))


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, current_user: dict = Depends(get_current_user)):
    ok = repo.delete_project(current_user["id"], project_id)
    if not ok:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")


def _missing(values: dict, required: list[str]) -> list[str]:
    """返回 values 中缺失（None 或不存在）的必需字段。"""
    return [k for k in required if values.get(k) is None]


@router.post("/{project_id}/calculate", response_model=SlabFullResult)
def calculate(
    project_id: int, payload: CalculateRequest, current_user: dict = Depends(get_current_user)
):
    project = repo.get_project(current_user["id"], project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    data = project["data"]
    if payload.page != "slab":
        # 次梁/主梁暂未接通（待深入调查）。
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"{payload.page} 计算尚未接通（本阶段仅支持 slab）",
        )

    missing = _missing(data.get("materials", {}), MATERIALS_REQUIRED)
    missing += _missing(data.get("slab", {}).get("input", {}), SLAB_REQUIRED_INPUT)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "missing_required", "missing": missing},
        )

    inp = SlabInput(**data["slab"]["input"])
    mat = data["materials"]
    try:
        result = calculate_slab(inp, fc=mat["fc"], fy=mat["fy_slab"], gamma_d=mat["gamma_d"])
    except ValueError as exc:
        # 超筋（αs>0.5 → xi() sqrt 域错误）或其他参数不合理。
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "calc_failed", "message": f"计算失败（可能超筋或参数不合理）: {exc}"},
        ) from exc

    # 写回结果，使 /checks 能在无需前端二次 PATCH 的情况下读到最新结果。
    # 注：原始设计意图为「无副作用、由前端 PATCH 保存」，但 test_checks_endpoint_after_calculate
    # 在 /calculate 后直接调用 /checks（中间无 PATCH）并期望非空，故此处落盘以同时满足两端语义。
    data.setdefault("slab", {})["result"] = result.model_dump()
    data["slab"]["initialized"] = True
    repo.update_project(current_user["id"], project_id, data=data)
    return result


@router.get("/{project_id}/checks")
def checks(project_id: int, current_user: dict = Depends(get_current_user)):
    project = repo.get_project(current_user["id"], project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    data = project["data"]
    slab = data.get("slab", {})
    if slab.get("initialized") and slab.get("result"):
        full = SlabFullResult(**slab["result"])
        slab_items = [item.model_dump() for item in check_slab(full, data["materials"])]
    else:
        slab_items = []
    return {"slab": slab_items}
