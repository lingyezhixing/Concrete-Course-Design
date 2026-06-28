"""主梁计算 — Pydantic 数据模型

配筋结果模型复用次梁的（BeamFlexureResult / ShearDesignResult），
因为次梁与主梁的正截面、斜截面配筋结果字段完全一致。
"""
from pydantic import BaseModel, Field

from app.models.beam import BeamFlexureResult, ShearDesignResult

__all__ = [
    "MainBeamInput",
    "MainBeamLoadOutput",
    "MainBeamInternalForceOutput",
    "MainBeamReinforcementOutput",
    "MainBeamFullResult",
]


class MainBeamInput(BaseModel):
    """主梁计算输入参数（几何 + 由结构/荷载派生的集中力分量）。

    集中力分量由 ``derive_main_beam_input`` 从统一 structure+loads 推导，
    不再由前端逐项填写。
    """

    # 几何
    span: float = Field(description="主梁跨度 (m)")
    beam_width: float = Field(description="主梁宽度 (mm)")
    beam_height: float = Field(description="主梁高度 (mm)")
    slab_thickness: float = Field(description="板厚 (mm)")
    column_width: float = Field(description="柱宽 (mm)")
    spans: int = Field(default=3, description="跨数（当前仅支持 3）")
    beam_spacing: float = Field(description="次梁间距 (m) = 翼缘宽 bf/1000")

    # 集中力分量（派生）
    from_beam_dead: float = Field(description="次梁传来恒载集中力 (kN)")
    self_weight: float = Field(description="主梁自重集中力 (kN)")
    plaster: float = Field(description="主梁粉刷集中力 (kN)")
    live_load: float = Field(description="活载集中力 (kN)")

    dead_load_factor: float = Field(default=1.05)
    live_load_factor: float = Field(default=1.20)


class MainBeamLoadOutput(BaseModel):
    """主梁荷载计算结果（集中力）"""

    from_beam_dead: float = Field(description="由次梁传来恒载 (kN)")
    self_weight: float = Field(description="主梁自重 (kN)")
    plaster: float = Field(description="主梁粉刷 (kN)")
    dead_load_standard: float = Field(description="恒载标准值 Gk (kN)")
    dead_load_design: float = Field(description="恒载设计值 G (kN)")
    live_load_standard: float = Field(description="活载标准值 Qk (kN)")
    live_load_design: float = Field(description="活载设计值 Q (kN)")


class MainBeamInternalForceOutput(BaseModel):
    """主梁内力计算结果（最不利组合包络）"""

    M1_max: float = Field(description="跨1最大正弯矩 (kN·m)")
    M2_max: float = Field(description="跨2最大正弯矩 (kN·m)")
    M_B_min: float = Field(description="支座B最小负弯矩 (kN·m)")
    M_C_min: float = Field(description="支座C最小负弯矩 (kN·m)")
    VA_max: float = Field(description="端支座A最大剪力 (kN)")
    VBl_min: float = Field(description="支座B左侧最小剪力 (kN)")
    VBr_max: float = Field(description="支座B右侧最大剪力 (kN)")


class MainBeamReinforcementOutput(BaseModel):
    """主梁配筋结果汇总"""

    flexure: list[BeamFlexureResult] = Field(description="正截面配筋")
    shear: ShearDesignResult = Field(description="斜截面箍筋及吊筋")


class MainBeamFullResult(BaseModel):
    """主梁完整计算结果（编排函数聚合，供 API 返回）。"""

    load: MainBeamLoadOutput
    internal_forces: MainBeamInternalForceOutput
    reinforcement: MainBeamReinforcementOutput
