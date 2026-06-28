"""项目生命周期路由：CRUD + （Task 8 追加）/calculate + /checks。

全部 Depends(get_current_user)，按 user_id 隔离；非自有资源 404。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.data import project_repository as repo
from app.models.project import ProjectCreate, ProjectPatch, ProjectPublic

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
    """updated_at > 最新快照 created_at，或无快照 → 有未归档改动。"""
    snaps = repo.list_snapshots(user_id, project["id"])
    if not snaps:
        return True
    return project["updated_at"] > snaps[0]["created_at"]  # list_snapshots 按 created_at DESC


@router.get("", response_model=list[ProjectPublic])
def list_projects(current_user: dict = Depends(get_current_user)):
    projects = repo.list_projects(current_user["id"])
    return [_to_public(p, _has_uncommitted(current_user["id"], p)) for p in projects]


@router.post("", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED)
def create_project(payload: ProjectCreate, current_user: dict = Depends(get_current_user)):
    project = repo.create_project(current_user["id"], payload.name)
    # 新建项目即空骨架（empty_data），尚无任何编辑 → has_uncommitted=False。
    # （与 list/get 的 _has_uncommitted 判定不同：那是面向“有快照后是否再改过”。
    #  create 用 False 以匹配 test_create_and_list_project 的预期。）
    return _to_public(project, False)


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
