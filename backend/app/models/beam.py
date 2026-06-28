"""次梁计算 — Pydantic 数据模型"""

import math

from pydantic import BaseModel, Field

__all__ = [
    "BeamInput",
    "BeamLoadOutput",
    "BeamSpanOutput",
    "BeamNetSpanOutput",
    "BeamLoadConvertOutput",
    "BeamMomentResult",
    "BeamShearResult",
    "BeamInternalForceOutput",
    "BeamFullResult",
]


class BeamInput(BaseModel):
    """次梁计算输入参数"""

    # 几何参数
    span: float = Field(description="次梁跨度 (m)")
    beam_width: float = Field(description="次梁宽度 (mm)")
    beam_height: float = Field(description="次梁高度 (mm)")
    slab_thickness: float = Field(description="板厚 (mm)")
    support_width: float = Field(default=250, description="支座宽度 / 主梁宽度 (mm)")
    spans: int = Field(default=5, description="跨数")
    wall_thickness: float = Field(default=370, description="墙体厚度 (mm)")
    bearing_length: float = Field(default=240, description="次梁搁置长度 (mm)")

    # 荷载参数（来自板计算的输出 + 次梁自身参数）
    slab_dead_load_standard: float = Field(description="板恒载标准值 (kN/m²)")
    live_load_per_area: float = Field(description="楼面活荷载标准值 (kN/m²)")
    beam_spacing: float = Field(description="次梁间距 (m)")

    concrete_weight: float = Field(default=25.0, description="钢筋混凝土重度 (kN/m³)")
    plaster_thickness: float = Field(default=15, description="抹灰厚度 (mm)")
    plaster_weight: float = Field(default=17.0, description="抹灰重度 (kN/m³)")

    # 分项系数
    dead_load_factor: float = Field(default=1.05, description="恒载分项系数")
    live_load_factor: float = Field(default=1.2, description="活载分项系数")

    # 构造参数
    stirrup_diameter: int | None = Field(default=None, description="箍筋直径 (mm)")


class BeamLoadOutput(BaseModel):
    """次梁荷载计算结果"""

    from_slab_dead: float = Field(description="由板传来恒载 (kN/m)")
    self_weight: float = Field(description="次梁自重 (kN/m)")
    plaster: float = Field(description="次梁粉刷 (kN/m)")

    dead_load_standard: float = Field(description="恒载标准值 gk (kN/m)")
    dead_load_design: float = Field(description="恒载设计值 g (kN/m)")

    live_load_standard: float = Field(description="活载标准值 qk (kN/m)")
    live_load_design: float = Field(description="活载设计值 q (kN/m)")


class BeamSpanOutput(BaseModel):
    """次梁计算跨度结果"""

    middle_span: float = Field(description="中间跨计算跨度 l0 (m)")
    edge_span: float = Field(description="边跨计算跨度 l0 = ln + (a+b)/2 (m)")


class BeamNetSpanOutput(BaseModel):
    """次梁净跨度结果"""

    middle_net: float = Field(description="中间跨净跨度 ln (m)")
    edge_net: float = Field(description="边跨净跨度 ln (m)")


class BeamLoadConvertOutput(BaseModel):
    """次梁荷载折算结果

    次梁: g' = g + q/4,  q' = 3q/4
    """

    converted_dead: float = Field(description="折算恒荷载 g' = g + q/4 (kN/m)")
    converted_live: float = Field(description="折算活荷载 q' = 3q/4 (kN/m)")


class BeamMomentResult(BaseModel):
    """单个位置的弯矩结果"""

    name: str = Field(description="位置名称")
    value: float = Field(description="弯矩设计值 (kN·m)")


class BeamShearResult(BaseModel):
    """单个位置的剪力结果"""

    name: str = Field(description="位置名称")
    value: float = Field(description="剪力设计值 (kN)")


class BeamInternalForceOutput(BaseModel):
    """次梁内力计算结果"""

    moments: list[BeamMomentResult] = Field(description="各位置弯矩")
    shears: list[BeamShearResult] = Field(description="各位置剪力")


# ──────────────────────────────────────────────
# 次梁配筋模型
# ──────────────────────────────────────────────


class BeamBarBundle(BaseModel):
    """梁钢筋束：n 根直径 d 的钢筋"""

    count: int = Field(description="钢筋根数")
    diameter: int = Field(description="钢筋直径 (mm)")

    @property
    def area(self) -> float:
        """总钢筋面积 (mm²)"""
        return self.count * math.pi * self.diameter**2 / 4

    @property
    def display(self) -> str:
        return f"{self.count}Φ{self.diameter}"


class BeamFlexureResult(BaseModel):
    """次梁正截面配筋结果"""

    name: str = Field(description="截面名称")
    moment: float = Field(description="弯矩设计值 (kN·m)")
    h0: float = Field(description="有效高度 (mm)")
    section_type: str = Field(description="截面类型: T形(第一类) / 矩形")
    width_used: float = Field(description="计算采用的截面宽度 (mm)")
    alpha_s: float = Field(description="截面抵抗矩系数 αs")
    xi: float = Field(description="相对受压区高度 ξ")
    as_required: float = Field(description="所需钢筋面积 (mm²)")
    selected_bar: BeamBarBundle | None = Field(description="选用的钢筋束")
    as_provided: float = Field(description="实配钢筋面积 (mm²)")
    status: str = Field(description="状态")
    candidates: list[BeamBarBundle] = Field(description="候选方案")


class ShearDesignResult(BaseModel):
    """梁斜截面箍筋计算结果（次梁、主梁共用）"""

    max_shear: float = Field(description="最大剪力设计值 (kN)")
    h0: float = Field(description="有效高度 (mm)")
    vc: float = Field(description="混凝土受剪承载力 (kN)")
    need_stirrups: bool = Field(description="是否需要计算配箍")
    asv_s: float = Field(description="计算所需 Asv/s (mm²/mm)")
    stirrup_diameter: int = Field(description="箍筋直径 (mm)")
    stirrup_legs: int = Field(description="箍筋肢数")
    asv: float = Field(description="单肢箍筋面积 × 肢数 (mm²)")
    recommended_spacing: float = Field(description="推荐箍筋间距 (mm)")
    stirrup_ratio: float = Field(description="箍筋配筋率")
    hanger_area: float = Field(default=0.0, description="吊筋所需面积 (mm²)，主梁使用")


class BeamReinforcementOutput(BaseModel):
    """次梁配筋计算结果"""

    flexure: list[BeamFlexureResult] = Field(description="各截面正截面配筋结果")
    shear: ShearDesignResult = Field(description="斜截面箍筋计算结果")


class BeamFullResult(BaseModel):
    """次梁完整计算结果（编排函数聚合，供 API 返回）。"""

    load: BeamLoadOutput
    span: BeamSpanOutput
    net_span: BeamNetSpanOutput
    converted: BeamLoadConvertOutput
    internal_forces: BeamInternalForceOutput
    reinforcement: BeamReinforcementOutput
