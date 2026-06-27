"""板计算 — Pydantic 数据模型"""

from pydantic import BaseModel, Field

__all__ = [
    "SlabInput",
    "SlabLoadOutput",
    "SlabSpanOutput",
    "SlabNetSpanOutput",
    "SlabLoadConvertOutput",
    "SlabMomentResult",
    "SlabShearResult",
    "SlabInternalForceOutput",
]


class SlabInput(BaseModel):
    """板计算输入参数"""

    # 几何参数
    length: float = Field(description="板的长度 (m)")
    width: float = Field(description="板的宽度 (m)")
    thickness: float = Field(description="板的厚度 (mm)")
    support_width: float = Field(description="支座宽度 / 次梁宽度 (mm)")
    spans: int = Field(description="跨数 (≥ 2，> 5 时按 5 跨查系数)")

    # 荷载参数
    reinforced_concrete_weight: float = Field(description="钢筋混凝土重度 (kN/m³)")
    terrazzo_surface: float = Field(description="水磨石面层 (kN/m²)")
    plaster_thickness: float = Field(description="抹灰厚度 (mm)")
    plaster_weight: float = Field(description="抹灰重度 (kN/m³)")
    live_load: float = Field(description="楼面活荷载 (kN/m²)")

    # 分项系数
    dead_load_factor: float = Field(default=1.05, description="恒载分项系数")
    live_load_factor: float = Field(default=1.2, description="活载分项系数")


class SlabLoadOutput(BaseModel):
    """板荷载计算结果"""

    # 恒载分项
    terrazzo: float = Field(description="水磨石面层 (kN/m²)")
    concrete: float = Field(description="钢筋混凝土板自重 (kN/m²)")
    plaster: float = Field(description="抹灰层 (kN/m²)")

    # 恒载
    dead_load_standard: float = Field(description="恒载标准值 qGk (kN/m²)")
    dead_load_design: float = Field(description="恒载设计值 qG (kN/m²)")

    # 活荷载
    live_load_standard: float = Field(description="活荷载标准值 qQk (kN/m²)")
    live_load_design: float = Field(description="活荷载设计值 qQ (kN/m²)")

    # 总荷载（取 1 米板带，kN/m）
    total_load: float = Field(description="荷载设计值 q = (qG + qQ) × 1m (kN/m)")


class SlabSpanOutput(BaseModel):
    """板计算跨度结果"""

    middle_span: float = Field(description="中间跨计算跨度 l0 (m)")
    edge_span: float = Field(description="边跨计算跨度 l0 = L/n - 0.120 + h/2 (m)")


class SlabNetSpanOutput(BaseModel):
    """板净跨度结果"""

    middle_net: float = Field(description="中间跨净跨度 ln = L/n - b (m)")
    edge_net: float = Field(description="边跨净跨度 ln = L/n - 0.120 - b/2 (m)")


class SlabLoadConvertOutput(BaseModel):
    """板荷载折算结果"""

    converted_dead: float = Field(description="折算恒荷载 g = qG + qQ/2 (kN/m)")
    converted_live: float = Field(description="折算活荷载 q = qQ/2 (kN/m)")


class SlabMomentResult(BaseModel):
    """单个位置的弯矩结果"""

    name: str = Field(description="位置名称，如 M1, MB, M2...")
    value: float = Field(description="弯矩设计值 (kN·m/m)")


class SlabShearResult(BaseModel):
    """单个位置的剪力结果"""

    name: str = Field(description="位置名称，如 VA, Vl_B, Vr_B, VC...")
    value: float = Field(description="剪力设计值 (kN/m)")


class SlabInternalForceOutput(BaseModel):
    """板内力计算结果（弯矩 + 剪力）"""

    moments: list[SlabMomentResult] = Field(description="各位置弯矩")
    shears: list[SlabShearResult] = Field(description="各位置剪力")


# ──────────────────────────────────────────────
# 配筋计算模型
# ──────────────────────────────────────────────


class ReinforcementBar(BaseModel):
    """钢筋规格（直径 + 间距）"""

    diameter: int = Field(description="钢筋直径 (mm)")
    spacing: int = Field(description="钢筋间距 (mm)")

    @property
    def area_per_meter(self) -> float:
        """每米板宽的钢筋面积 (mm²/m)"""
        import math
        return math.pi * self.diameter**2 / 4 * (1000 / self.spacing)

    @property
    def display(self) -> str:
        """显示名称，如 Φ8@200"""
        return f"Φ{self.diameter}@{self.spacing}"


class SectionReinforcement(BaseModel):
    """单个截面的配筋计算结果"""

    name: str = Field(description="截面名称")
    moment: float = Field(description="弯矩设计值 (kN·m)")
    h0: float = Field(description="有效高度 (mm)")
    alpha_s: float = Field(description="截面抵抗矩系数 αs")
    xi: float = Field(description="相对受压区高度 ξ")
    as_required: float = Field(description="所需钢筋面积 (mm²)")
    selected_bar: ReinforcementBar | None = Field(description="选用的钢筋方案")
    as_provided: float = Field(description="实配钢筋面积 (mm²)")
    status: str = Field(description="状态：推荐 / 建议复核 / 不足")
    candidates: list[ReinforcementBar] = Field(description="满足要求的候选方案")


class SlabReinforcementOutput(BaseModel):
    """板配筋计算结果汇总"""

    sections: list[SectionReinforcement] = Field(description="各截面配筋结果")
