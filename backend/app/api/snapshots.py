"""快照路由：归档 / 列表 / 恢复 / fork / 删除。全部按 user_id 隔离。"""

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.data import project_repository as repo
from app.models.project import ProjectPublic, SnapshotCreate, SnapshotPublic

router = APIRouter(tags=["snapshots"])


def _require_project(user_id: int, project_id: int) -> None:
    """快照端点先确认项目存在且属于本人，否则 404。"""
    if repo.get_project(user_id, project_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="项目不存在")


@router.get("/projects/{project_id}/snapshots", response_model=list[SnapshotPublic])
def list_snapshots(project_id: int, current_user: dict = Depends(get_current_user)):
    _require_project(current_user["id"], project_id)
    return [SnapshotPublic(**s) for s in repo.list_snapshots(current_user["id"], project_id)]


@router.post(
    "/projects/{project_id}/snapshots", response_model=SnapshotPublic, status_code=status.HTTP_201_CREATED
)
def create_snapshot(
    project_id: int, payload: SnapshotCreate, current_user: dict = Depends(get_current_user)
):
    _require_project(current_user["id"], project_id)
    name = payload.name or "未命名归档"
    snap = repo.create_snapshot(current_user["id"], project_id, name)
    return SnapshotPublic(**snap)


@router.post("/projects/{project_id}/snapshots/{snapshot_id}/restore", response_model=ProjectPublic)
def restore_snapshot(project_id: int, snapshot_id: int, current_user: dict = Depends(get_current_user)):
    _require_project(current_user["id"], project_id)
    project = repo.restore_snapshot(current_user["id"], project_id, snapshot_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")
    return ProjectPublic(
        id=project["id"], name=project["name"], data=project["data"],
        created_at=project["created_at"], updated_at=project["updated_at"],
        last_opened_at=project["last_opened_at"], has_uncommitted=False,
    )


@router.post(
    "/projects/{project_id}/snapshots/{snapshot_id}/fork", response_model=ProjectPublic, status_code=status.HTTP_201_CREATED
)
def fork_snapshot(
    project_id: int, snapshot_id: int, payload: SnapshotCreate, current_user: dict = Depends(get_current_user)
):
    _require_project(current_user["id"], project_id)
    name = payload.name or "未命名副本"
    project = repo.fork_snapshot(current_user["id"], project_id, snapshot_id, name)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")
    return ProjectPublic(
        id=project["id"], name=project["name"], data=project["data"],
        created_at=project["created_at"], updated_at=project["updated_at"],
        last_opened_at=project["last_opened_at"], has_uncommitted=True,
    )


@router.delete("/snapshots/{snapshot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_snapshot(snapshot_id: int, current_user: dict = Depends(get_current_user)):
    if not repo.delete_snapshot(current_user["id"], snapshot_id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="快照不存在")
