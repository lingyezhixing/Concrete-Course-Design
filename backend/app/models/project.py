"""项目生命周期 API 的 Pydantic 模型 + 门禁必需字段常量。"""

from typing import Any, Literal

from pydantic import BaseModel, Field

# ──────────────────────────────────────────────
# 统一参数三段：structure / materials / loads
# 三构件的 Input 由 derive_* 在 /calculate 时从 structure+loads 派生。
# ──────────────────────────────────────────────


class StructureParams(BaseModel):
    """结构参数（第一部分）。L1∥次梁，L2∥主梁（= 板跨方向）。"""

    L1: float = Field(description="平面长边 L1 (m)，平行次梁")
    L2: float = Field(description="平面短边 L2 (m)，平行主梁/板跨方向")
    slab_thickness: float = Field(description="板厚 (mm)")
    beam_width: float = Field(description="次梁宽 (mm)")
    beam_height: float = Field(description="次梁高 (mm)")
    main_beam_width: float = Field(description="主梁宽 (mm)")
    main_beam_height: float = Field(description="主梁高 (mm)")
    column_width: float = Field(description="柱宽 (mm)")
    slab_spans: int = Field(description="板跨数（>5 按五跨连续板查系数）")
    beam_spans: int = Field(description="次梁跨数")
    main_beam_spans: int = Field(description="主梁跨数（当前仅支持 3）")


class LoadsParams(BaseModel):
    """荷载参数。恒载/活载分项系数已固定在后端（1.05 / 1.20）。"""

    reinforced_concrete_weight: float = Field(description="钢筋混凝土重度 (kN/m³)")
    terrazzo_surface: float = Field(description="水磨石面层 (kN/m²)")
    plaster_thickness: float = Field(description="抹灰厚度 (mm)")
    plaster_weight: float = Field(description="抹灰重度 (kN/m³)")
    live_load: float = Field(description="楼面活荷载 (kN/m²)")


# 门禁：用户必填的字段（材料与分项系数已固定在后端）。
STRUCTURE_REQUIRED = [
    "L1", "L2", "slab_thickness",
    "beam_width", "beam_height",
    "main_beam_width", "main_beam_height",
    "column_width", "slab_spans", "beam_spans", "main_beam_spans",
]
LOADS_REQUIRED = [
    "reinforced_concrete_weight", "terrazzo_surface",
    "plaster_thickness", "plaster_weight", "live_load",
]


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
