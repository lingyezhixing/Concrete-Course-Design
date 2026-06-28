"""统一参数 → 各构件 Input 的派生。

前端只存 ``structure`` / ``materials`` / ``loads`` 三段；本模块在 /calculate 时
由结构+荷载派生出 ``SlabInput`` / ``BeamInput`` / ``MainBeamInput``。

派生关系（几何）：
  - 次梁间距 = 板单跨 = L2 / slab_spans
  - 次梁跨度 = L1 / beam_spans
  - 主梁跨度 = L2 / main_beam_spans

三构件均从同一份 structure+loads 独立可算（无运行时输出依赖），
故一键级联只是按 板→次梁→主梁 顺序触发，非数据依赖。
"""

from __future__ import annotations

from app.models.beam import BeamInput
from app.models.main_beam import MainBeamInput
from app.models.project import LoadsParams, StructureParams
from app.models.slab import SlabInput

__all__ = [
    "slab_dead_load_standard",
    "derive_slab_input",
    "derive_beam_input",
    "derive_main_beam_input",
]


def slab_dead_load_standard(s: StructureParams, l: LoadsParams) -> float:
    """板恒载标准值 (kN/m²) = 水磨石 + 板自重 + 抹灰。三构件共用。"""
    return (
        l.terrazzo_surface
        + l.reinforced_concrete_weight * (s.slab_thickness / 1000.0)
        + l.plaster_weight * (l.plaster_thickness / 1000.0)
    )


def derive_slab_input(s: StructureParams, l: LoadsParams) -> SlabInput:
    """派生板输入。

    板以次梁为支座，单跨 = 次梁间距 = L2/slab_spans。实际跨数 > 5 时按课程惯例
    简化为**五跨连续板**模型：传 model_spans=min(slab_spans,5) 与
    width=单跨×model_spans，使求解器 l0=单跨 且输出五跨模型截面。
    分项系数已在后端固定：γG=1.05、γQ=1.2。
    """
    beam_spacing = s.L2 / s.slab_spans
    model_spans = min(s.slab_spans, 5)
    return SlabInput(
        length=s.L1,  # 板带长边，求解器不参与跨度计算（仅 width 用）
        width=beam_spacing * model_spans,  # → l0 = beam_spacing
        thickness=s.slab_thickness,
        support_width=s.beam_width,  # 板支座 = 次梁宽
        spans=model_spans,
        reinforced_concrete_weight=l.reinforced_concrete_weight,
        terrazzo_surface=l.terrazzo_surface,
        plaster_thickness=l.plaster_thickness,
        plaster_weight=l.plaster_weight,
        live_load=l.live_load,
        dead_load_factor=1.05,
        live_load_factor=1.20,
    )


def derive_beam_input(s: StructureParams, l: LoadsParams) -> BeamInput:
    """派生次梁输入。次梁单跨 = L1/beam_spans；支座 = 主梁宽；>5 跨按五跨简化。"""
    return BeamInput(
        span=s.L1 / s.beam_spans,
        beam_width=s.beam_width,
        beam_height=s.beam_height,
        slab_thickness=s.slab_thickness,
        support_width=s.main_beam_width,  # 次梁支座 = 主梁宽
        spans=min(s.beam_spans, 5),
        beam_spacing=s.L2 / s.slab_spans,
        slab_dead_load_standard=slab_dead_load_standard(s, l),
        live_load_per_area=l.live_load,
        concrete_weight=l.reinforced_concrete_weight,
        plaster_thickness=l.plaster_thickness,
        plaster_weight=l.plaster_weight,
        dead_load_factor=1.05,
        live_load_factor=1.20,
    )


def derive_main_beam_input(s: StructureParams, l: LoadsParams) -> MainBeamInput:
    """派生主梁输入，并推导集中力分量。

    - from_beam_dead = 次梁恒载标准值 × 次梁跨度（次梁端反力 = 总恒载）
    - self_weight / plaster = 主梁腹板(扣板厚) × 次梁间距
    - live_load = 楼面活载 × 从属面积(次梁跨度 × 次梁间距)
    分项系数已在后端固定：γG=1.05、γQ=1.2。
    """
    beam_spacing = s.L2 / s.slab_spans
    sec_span = s.L1 / s.beam_spans  # 次梁跨度

    # 次梁恒载标准值 gk（板传 + 次梁自重 + 次梁粉刷）
    sec_from_slab = slab_dead_load_standard(s, l) * beam_spacing
    sec_dh = (s.beam_height - s.slab_thickness) / 1000.0
    sec_self = l.reinforced_concrete_weight * (s.beam_width / 1000.0) * sec_dh
    sec_plaster = l.plaster_weight * (l.plaster_thickness / 1000.0) * sec_dh * 2
    sec_gk = sec_from_slab + sec_self + sec_plaster

    from_beam_dead = sec_gk * sec_span

    # 主梁自重 / 粉刷（腹板高 × 次梁间距，板厚部分已由板承担）
    mb_dh = (s.main_beam_height - s.slab_thickness) / 1000.0
    self_weight = l.reinforced_concrete_weight * (s.main_beam_width / 1000.0) * mb_dh * beam_spacing
    plaster = l.plaster_weight * (l.plaster_thickness / 1000.0) * mb_dh * beam_spacing * 2

    live_load_force = l.live_load * sec_span * beam_spacing  # 从属面积法

    return MainBeamInput(
        span=s.L2 / s.main_beam_spans,
        beam_width=s.main_beam_width,
        beam_height=s.main_beam_height,
        slab_thickness=s.slab_thickness,
        column_width=s.column_width,
        spans=s.main_beam_spans,
        beam_spacing=beam_spacing,
        from_beam_dead=from_beam_dead,
        self_weight=self_weight,
        plaster=plaster,
        live_load=live_load_force,
        dead_load_factor=1.05,
        live_load_factor=1.20,
    )
