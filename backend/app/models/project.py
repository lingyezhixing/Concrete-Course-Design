"""项目生命周期 API 的 Pydantic 模型 + 门禁必需字段常量。"""

from typing import Any, Literal

from pydantic import BaseModel, Field

# 门禁：无默认值、用户必填的 input 字段（有 Pydantic 默认的不计入）。
# 与 SlabInput / BeamInput / MainBeamInput 的无默认字段一一对应。
SLAB_REQUIRED_INPUT = [
    "length",
    "width",
    "thickness",
    "support_width",
    "spans",
    "reinforced_concrete_weight",
    "terrazzo_surface",
    "plaster_thickness",
    "plaster_weight",
    "live_load",
]
MATERIALS_REQUIRED = ["fc", "fy_slab", "gamma_d"]


class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class ProjectPatch(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    data: dict[str, Any] | None = None


class ProjectPublic(BaseModel):
    id: int
    name: str
    data: dict[str, Any]
    created_at: str
    updated_at: str
    last_opened_at: str | None = None
    has_uncommitted: bool = False


class SnapshotCreate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)


class SnapshotPublic(BaseModel):
    id: int
    project_id: int
    name: str
    data: dict[str, Any]
    created_at: str


class CalculateRequest(BaseModel):
    page: Literal["slab", "beam", "main_beam"]
