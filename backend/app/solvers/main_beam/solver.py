"""主梁 — 荷载、内力、配筋求解器"""

from app.models.main_beam import (
    MainBeamFullResult,
    MainBeamInput,
    MainBeamLoadOutput,
    MainBeamInternalForceOutput,
    MainBeamReinforcementOutput,
)
from app.solvers.main_beam.utils import (
    calc_envelope,
    calc_main_beam_flexure,
    calc_main_beam_shear,
)

__all__ = [
    "calculate_main_beam_load",
    "calculate_main_beam_internal_forces",
    "calculate_main_beam_reinforcement",
    "calculate_main_beam",
]


def calculate_main_beam_load(
    from_beam_dead: float,
    self_weight: float,
    plaster: float,
    live_load: float,
    dead_load_factor: float = 1.05,
    live_load_factor: float = 1.20,
) -> MainBeamLoadOutput:
    """主梁荷载计算（集中力）。

    主梁集中力 = 次梁支座反力 + 主梁自重折算 + 粉刷
    """
    gk = from_beam_dead + self_weight + plaster
    g = dead_load_factor * gk
    qk = live_load
    q = live_load_factor * qk

    return MainBeamLoadOutput(
        from_beam_dead=round(from_beam_dead, 4),
        self_weight=round(self_weight, 4),
        plaster=round(plaster, 4),
        dead_load_standard=round(gk, 4),
        dead_load_design=round(g, 4),
        live_load_standard=round(qk, 4),
        live_load_design=round(q, 4),
    )


def calculate_main_beam_internal_forces(
    dead_load: float,
    live_load: float,
    span: float,
    support_width: float = 350,
) -> MainBeamInternalForceOutput:
    """主梁内力计算，4种荷载布置取最不利包络。

    计算跨度（教师示例约定）：
      - 边跨跨中（M1）：L₁ = 轴线跨 span
      - 中跨跨中（M2）及支座（M_B, M_C）：L₂ = 1.05 × (轴线 − 柱宽)

    支座弯矩做边缘调整：M' = M + (b/2) × V₀，
    其中 V₀ 取简支梁支座剪力 (G+Q)/2（support_width 即柱宽，单位 mm）。
    """
    b_col = support_width / 1000.0       # 柱宽 (m)
    l0_edge = span                        # 边跨：轴线跨
    l0_interior = 1.05 * (span - b_col)   # 中跨及支座：1.05×(轴线−柱宽)

    env = calc_envelope(G=dead_load, Q=live_load, l0_edge=l0_edge, l0_interior=l0_interior)

    # 支座边缘弯矩调整：V₀ = (G+Q)/2（简支梁支座剪力）
    v0 = (dead_load + live_load) / 2.0
    m_b_adj = env["M_B"] + (b_col / 2.0) * v0
    m_c_adj = env["M_C"] + (b_col / 2.0) * v0

    return MainBeamInternalForceOutput(
        M1_max=round(env["M1"], 4),
        M2_max=round(env["M2"], 4),
        M_B_min=round(m_b_adj, 4),
        M_C_min=round(m_c_adj, 4),
        VA_max=round(env["VA"], 4),
        VBl_min=round(env["VBl"], 4),
        VBr_max=round(env["VBr"], 4),
    )


def calculate_main_beam_reinforcement(
    dead_load: float,
    live_load: float,
    span: float,
    support_width: float = 350,
    h: float = 500,
    b: float = 250,
    bf: float = 2000,
    hf: float = 80,
    cover: float = 30,
    bar_diameter: float = 20,
    fc: float = 9.6,
    ft: float = 1.10,
    fy: float = 300,
    gamma_d: float = 1.20,
    stirrup_diameter: int = 10,
    stirrup_legs: int = 2,
    fyv: float = 270,
    hanger_force: float | None = None,
) -> MainBeamReinforcementOutput:
    """主梁完整配筋计算"""

    forces = calculate_main_beam_internal_forces(
        dead_load=dead_load, live_load=live_load,
        span=span, support_width=support_width,
    )

    # 正截面
    flexure_sections = [
        ("1", forces.M1_max, True),
        ("B", abs(forces.M_B_min), True),
        ("2", forces.M2_max, True),
    ]

    flexure_results = []
    for name, moment, use_t in flexure_sections:
        r = calc_main_beam_flexure(
            name=name, moment=moment,
            h=h, b=b, bf=bf, hf=hf,
            cover=cover, bar_diameter=bar_diameter,
            fc=fc, fy=fy, gamma_d=gamma_d,
            use_t_section=use_t,
        )
        flexure_results.append(r)

    # 斜截面（取最大剪力）
    max_v = max(abs(forces.VA_max), abs(forces.VBl_min), abs(forces.VBr_max))

    shear_result = calc_main_beam_shear(
        max_shear=max_v,
        b=b, h=h, cover=cover, bar_diameter=bar_diameter,
        ft=ft, gamma_d=gamma_d,
        stirrup_diameter=stirrup_diameter,
        stirrup_legs=stirrup_legs,
        fyv=fyv,
        hanger_force=hanger_force,
    )

    return MainBeamReinforcementOutput(
        flexure=flexure_results,
        shear=shear_result,
    )


def calculate_main_beam(
    inp: MainBeamInput,
    fc: float,
    fy: float,
    gamma_d: float,
    ft: float = 1.10,
    cover: float = 30.0,
    bar_diameter: float = 20.0,
    stirrup_legs: int = 2,
    fyv: float = 270,
) -> MainBeamFullResult:
    """主梁完整计算编排：荷载 → 内力 → 正截面 → 斜截面（含吊筋）。

    集中力分量已在 ``MainBeamInput``（由 ``derive_main_beam_input`` 填好）；
    本函数串联 load → reinforcement，并按次梁设计反力计算吊筋集中力。
    课程简化：全部截面按 T 形（翼缘宽 bf = 次梁间距×1000）。
    """
    load = calculate_main_beam_load(
        from_beam_dead=inp.from_beam_dead,
        self_weight=inp.self_weight,
        plaster=inp.plaster,
        live_load=inp.live_load,
        dead_load_factor=inp.dead_load_factor,
        live_load_factor=inp.live_load_factor,
    )

    bf = inp.beam_spacing * 1000.0  # 翼缘宽 = 次梁间距 (mm)
    hf = inp.slab_thickness

    # 吊筋承担次梁传来的集中力（恒载+活载设计值），不含主梁自重/粉刷（分布荷载）
    hanger_force = load.from_beam_dead * inp.dead_load_factor + inp.live_load * inp.live_load_factor

    internal_forces = calculate_main_beam_internal_forces(
        dead_load=load.dead_load_design,
        live_load=load.live_load_design,
        span=inp.span,
        support_width=inp.column_width,
    )

    reinforcement = calculate_main_beam_reinforcement(
        dead_load=load.dead_load_design,
        live_load=load.live_load_design,
        span=inp.span,
        support_width=inp.column_width,
        h=inp.beam_height,
        b=inp.beam_width,
        bf=bf,
        hf=hf,
        cover=cover,
        bar_diameter=bar_diameter,
        fc=fc,
        ft=ft,
        fy=fy,
        gamma_d=gamma_d,
        stirrup_diameter=inp.stirrup_diameter,
        stirrup_legs=stirrup_legs,
        fyv=fyv,
        hanger_force=hanger_force,
    )

    return MainBeamFullResult(
        load=load, internal_forces=internal_forces, reinforcement=reinforcement,
    )
