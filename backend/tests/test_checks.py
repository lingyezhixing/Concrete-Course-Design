"""板规范校核 check_slab：ξ≤ξb、ρ≥ρmin、As实≥As需。"""

from app.checks import check_slab
from app.models.slab import (
    ReinforcementBar,
    SectionReinforcement,
    SlabFullResult,
    SlabInternalForceOutput,
    SlabLoadConvertOutput,
    SlabLoadOutput,
    SlabNetSpanOutput,
    SlabReinforcementOutput,
    SlabSpanOutput,
)


def _full(sections):
    return SlabFullResult(
        load=SlabLoadOutput(
            terrazzo=0, concrete=0, plaster=0, dead_load_standard=0,
            dead_load_design=0, live_load_standard=0, live_load_design=0, total_load=0,
        ),
        span=SlabSpanOutput(middle_span=0, edge_span=0),
        net_span=SlabNetSpanOutput(middle_net=0, edge_net=0),
        converted=SlabLoadConvertOutput(converted_dead=0, converted_live=0),
        internal_forces=SlabInternalForceOutput(moments=[], shears=[]),
        reinforcement=SlabReinforcementOutput(sections=sections),
    )


def _section(name, xi, h0, as_required, as_provided, status):
    return SectionReinforcement(
        name=name, moment=0, h0=h0, alpha_s=0, xi=xi,
        as_required=as_required,
        selected_bar=ReinforcementBar(diameter=8, spacing=200) if as_provided else None,
        as_provided=as_provided, status=status, candidates=[],
    )


MATERIALS = {"fc": 9.6, "fy_slab": 270, "fy_beam": 300, "gamma_d": 1.2}


def test_passing_section_all_green():
    # ξ=0.12<ξb(0.568); ρ: As=251.3,h0=55 → 0.00457>0.002; As实>As需; status 推荐
    sec = _section("M1", xi=0.12, h0=55, as_required=228.5, as_provided=251.3, status="推荐")
    items = check_slab(_full([sec]), MATERIALS)
    statuses = {i.name: i.status for i in items}
    assert all(s == "pass" for s in statuses.values())


def test_xi_exceeds_xi_b_fails():
    sec = _section("M1", xi=0.70, h0=55, as_required=228.5, as_provided=251.3, status="推荐")
    items = check_slab(_full([sec]), MATERIALS)
    xi_item = next(i for i in items if "ξ" in i.name)
    assert xi_item.status == "fail"


def test_rho_below_min_fails():
    # As_provided 很小 → ρ<ρmin
    sec = _section("M1", xi=0.12, h0=55, as_required=228.5, as_provided=20.0, status="不足")
    items = check_slab(_full([sec]), MATERIALS)
    rho_item = next(i for i in items if "ρ" in i.name)
    assert rho_item.status == "fail"


def test_over_reinforcement_is_review():
    # status="建议复核"（超配>1.8）→ As 项为 review
    sec = _section("M1", xi=0.12, h0=55, as_required=100.0, as_provided=400.0, status="建议复核")
    items = check_slab(_full([sec]), MATERIALS)
    as_item = next(i for i in items if "As" in i.name)
    assert as_item.status == "review"
