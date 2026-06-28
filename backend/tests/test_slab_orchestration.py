"""板编排函数 calculate_slab：串联现有步骤 + 构造默认值。"""

import pytest

from app.models.slab import SlabInput
from app.solvers.common import effective_depth
from app.solvers.slab.solver import (
    calculate_internal_forces,
    calculate_load,
    calculate_slab,
    calculate_slab_reinforcement,
    calculate_spans,
    calculate_net_spans,
    convert_loads,
)


def _inp():
    # length≠width 以暴露跨度方向：板跨度沿 width(L₂) 方向，middle_span = width/spans = 6/3 = 2m；
    # length(L₁) 平行于次梁，仅作板带长边，不参与跨度计算。
    # 80mm 板上若误用 length/大跨，会使 αs>0.5 触发 sqrt 定义域错误（输入越界，非本编排函数职责）。
    return SlabInput(
        length=12.0, width=6.0, thickness=80, support_width=200, spans=3,
        reinforced_concrete_weight=25.0, terrazzo_surface=0.65,
        plaster_thickness=20, plaster_weight=17.0, live_load=2.0,
    )


def test_load_stage_matches_standalone():
    inp = _inp()
    result = calculate_slab(inp, fc=9.6, fy=270, gamma_d=1.2)
    assert result.load == calculate_load(inp)
    # 荷载手算: 恒载标准 = 0.65 + 0.08*25 + 0.02*17 = 2.99
    assert result.load.dead_load_standard == pytest.approx(2.99, abs=0.01)


def test_all_stages_present_and_composed():
    inp = _inp()
    result = calculate_slab(inp, fc=9.6, fy=270, gamma_d=1.2)
    assert result.span == calculate_spans(inp)
    assert result.net_span == calculate_net_spans(inp)
    assert result.converted == convert_loads(result.load)
    assert result.internal_forces == calculate_internal_forces(
        inp, result.load, result.span, result.net_span, result.converted
    )


def test_reinforcement_uses_internal_moments_and_default_cover():
    inp = _inp()
    result = calculate_slab(inp, fc=9.6, fy=270, gamma_d=1.2)
    # 配筋截面数 == 内力弯矩数
    assert len(result.reinforcement.sections) == len(result.internal_forces.moments)
    # h0 用构造默认 cover=20, bar_diameter=10
    expected_h0 = effective_depth(inp.thickness, 20, 10)
    assert result.reinforcement.sections[0].h0 == pytest.approx(expected_h0, abs=0.01)
    # 截面名沿用内力弯矩名（M1, M_B, ...）
    names = [s.name for s in result.reinforcement.sections]
    assert "M1" in names and "M_B" in names


def test_spans_derive_from_width_not_length():
    """板跨度沿 width(L₂) 方向：middle_span = width/spans，而非 length/spans。

    板以次梁为支座，跨度方向 ⊥ 次梁 = ∥ 主梁 = L₂(width)。length(L₁) 平行次梁，
    仅作板带长边。该测试用 length≠width 区分两者（此前 length=width=6 掩盖了方向）。
    """
    inp = SlabInput(
        length=12.0, width=6.0, thickness=80, support_width=200, spans=3,
        reinforced_concrete_weight=25.0, terrazzo_surface=0.65,
        plaster_thickness=20, plaster_weight=17.0, live_load=2.0,
    )
    spans = calculate_spans(inp)
    # 6/3 = 2.0（来自 width），不是 12/3 = 4.0（length）
    assert spans.middle_span == pytest.approx(2.0, abs=0.001)
    # edge_span = middle − 0.120 + h/2 = 2.0 − 0.12 + 0.04 = 1.92
    assert spans.edge_span == pytest.approx(1.92, abs=0.001)

    net = calculate_net_spans(inp)
    # middle_net = width/spans − b = 2.0 − 0.2 = 1.8
    assert net.middle_net == pytest.approx(1.8, abs=0.001)
    # edge_net = width/spans − 0.120 − b/2 = 2.0 − 0.12 − 0.1 = 1.78
    assert net.edge_net == pytest.approx(1.78, abs=0.001)
