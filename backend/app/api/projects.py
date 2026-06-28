"""项目生命周期路由：CRUD + /calculate（三构件派生计算）+ /checks（休眠）。

全部 Depends(get_current_user)，按 user_id 隔离；非自有资源 404。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.checks import check_slab
from app.data import project_repository as repo
from app.models.beam import BeamFullResult
from app.models.main_beam import MainBeamFullResult
from app.models.project import (
    CalculateRequest,
    LOADS_REQUIRED,
    ProjectCreate,
    ProjectPatch,
    ProjectPublic,
    STRUCTURE_REQUIRED,
    StructureParams,
    LoadsParams,
)
from app.models.slab import SlabFullResult
from app.solvers.beam.solver import calculate_beam
from app.solvers.derive import (
    derive_beam_input,
    derive_main_beam_input,
    derive_slab_input,
)
from app.solvers.main_beam.solver import calculate_main_beam
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


@router.post("/{project_id}/calculate")
def calculate(
    project_id: int, payload: CalculateRequest, current_user: dict = Depends(get_current_user)
):
    """按 page 由 structure+loads+materials 派生 Input 并计算，返回结果。

    支持三页：slab / beam / main_beam。前端「确认计算」一键级联调用三次。
    """
    project = repo.get_project(current_user["id"], project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")

    data = project["data"]

    # 门禁：structure + loads 必填字段齐全（材料与分项系数已固定在后端）
    missing = _missing(data.get("structure", {}), STRUCTURE_REQUIRED)
    missing += _missing(data.get("loads", {}), LOADS_REQUIRED)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "missing_required", "missing": missing},
        )

    structure = StructureParams(**data["structure"])
    loads = LoadsParams(**data["loads"])

    # 材料强度与分项系数固定值（C20 fc=9.6, ft=1.10, I级 fy=270, II级 fy=300, γd=1.2）
    FC = 9.6
    FT = 1.10
    FY_SLAB = 270
    FY_BEAM = 300
    GAMMA_D = 1.2

    try:
        if payload.page == "slab":
            result = calculate_slab(
                derive_slab_input(structure, loads),
                fc=FC, fy=FY_SLAB, gamma_d=GAMMA_D,
            )
            typed = SlabFullResult
        elif payload.page == "beam":
            result = calculate_beam(
                derive_beam_input(structure, loads),
                fc=FC, ft=FT, fy=FY_BEAM, gamma_d=GAMMA_D,
            )
            typed = BeamFullResult
        else:  # main_beam
            result = calculate_main_beam(
                derive_main_beam_input(structure, loads),
                fc=FC, ft=FT, fy=FY_BEAM, gamma_d=GAMMA_D,
            )
            typed = MainBeamFullResult
    except ValueError as exc:
        # 超筋（αs>0.5 → xi() sqrt 域错误）或其他参数不合理。
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "calc_failed", "message": f"计算失败（可能超筋或参数不合理）: {exc}"},
        ) from exc

    # 落盘结果（供休眠的 /checks 读取；前端亦会 PATCH 覆盖，幂等）。
    dumped = result.model_dump()
    comp = data.setdefault(payload.page, {"result": {}, "initialized": False})
    comp["result"] = dumped
    comp["initialized"] = True
    repo.update_project(current_user["id"], project_id, data=data)
    return typed.model_validate(dumped)


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
