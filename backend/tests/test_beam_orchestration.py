"""次梁编排函数 calculate_beam：串联现有步骤 + 构造默认值 + T/rect 截面。"""

import pytest

from app.models.beam import BeamInput
from app.solvers.beam.solver import (
    calculate_beam,
    calculate_beam_internal_forces,
    calculate_beam_load,
    calculate_beam_net_spans,
    calculate_beam_spans,
    convert_beam_loads,
)


def _inp():
    # 板传来荷载（跨页，由全链 /calculate 从板 result 填入；这里直接给值）
    return BeamInput(
        span=6.0, beam_width=200, beam_height=500, slab_thickness=80,
        slab_dead_load_standard=3.0, live_load_per_area=2.0, beam_spacing=2.0,
        stirrup_diameter=6,
    )


def test_load_stage_matches_standalone():
    inp = _inp()
    result = calculate_beam(inp, fc=9.6, fy=300, gamma_d=1.2)
    assert result.load == calculate_beam_load(inp)


def test_all_stages_present_and_composed():
    inp = _inp()
    result = calculate_beam(inp, fc=9.6, fy=300, gamma_d=1.2)
    assert result.span == calculate_beam_spans(inp)
    assert result.net_span == calculate_beam_net_spans(inp)
    assert result.converted == convert_beam_loads(result.load)
    assert result.internal_forces == calculate_beam_internal_forces(
        inp, result.load, result.span, result.net_span, result.converted
    )


def test_flexure_sections_match_moments_with_t_and_rect():
    inp = _inp()
    result = calculate_beam(inp, fc=9.6, fy=300, gamma_d=1.2)
    # 正截面数 == 内力弯矩数
    assert len(result.reinforcement.flexure) == len(result.internal_forces.moments)
    # 跨中正弯矩 → T 形；支座负弯矩 → 矩形（两种都应出现）
    section_types = {f.section_type for f in result.reinforcement.flexure}
    # 至少应有 T 形与矩形各一类（5 跨 → 跨中位置正弯矩、支座位置负弯矩）
    has_t = any("T形" in st for st in section_types)
    has_rect = any("矩形" in st for st in section_types)
    assert has_t and has_rect, section_types


def test_shear_uses_max_shear():
    inp = _inp()
    result = calculate_beam(inp, fc=9.6, fy=300, gamma_d=1.2)
    max_shear = max(abs(s.value) for s in result.internal_forces.shears)
    assert result.reinforcement.shear.max_shear == pytest.approx(max_shear, abs=0.01)
