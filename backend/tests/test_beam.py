"""次梁计算 — 测试"""
import math

import pytest

from app.models.beam import (
    BeamInput,
    BeamLoadOutput,
    BeamSpanOutput,
    BeamNetSpanOutput,
    BeamLoadConvertOutput,
    BeamInternalForceOutput,
    BeamBarBundle,
)


class TestBeamBarBundle:
    """梁钢筋束模型"""

    def test_area_calculation(self):
        """2Φ14: As = 2 × π × 14²/4 = 307.9 mm²"""
        bundle = BeamBarBundle(count=2, diameter=14)
        expected = 2 * math.pi * 14**2 / 4
        assert bundle.area == pytest.approx(expected, rel=1e-4)

    def test_display_name(self):
        """6Φ14 的显示名称"""
        bundle = BeamBarBundle(count=6, diameter=14)
        assert bundle.display == "6Φ14"


class TestBeamFlexure:
    """次梁正截面配筋计算"""

    def test_t_section_type1_m1(self):
        """M1=79.2364, T形第一类, bf=2000 → As=897.9"""
        from app.solvers.beam.utils import calc_beam_flexure

        result = calc_beam_flexure(
            name="1", moment=79.2364,
            section_type="T",
            b=200, bf=2000, h=400, hf=80,
            cover=30, bar_diameter=20,
            fc=9.6, fy=300, gamma_d=1.20,
        )
        assert result.section_type == "T形(第一类)"
        assert result.width_used == 2000
        assert result.as_required == pytest.approx(897.9, abs=1.0)

    def test_rectangular_section_mb(self):
        """MB=-92.8654, 矩形b=200 → As=1559.9"""
        from app.solvers.beam.utils import calc_beam_flexure

        result = calc_beam_flexure(
            name="B", moment=-92.8654,
            section_type="rect",
            b=200, bf=2000, h=400, hf=80,
            cover=30, bar_diameter=20,
            fc=9.6, fy=300, gamma_d=1.20,
        )
        assert result.section_type == "矩形"
        assert result.width_used == 200
        assert result.as_required == pytest.approx(1559.9, abs=1.0)

    def test_all_flexure_sections(self):
        """所有5个截面与参考网站一致"""
        from app.solvers.beam.utils import calc_beam_flexure

        ref = {
            "1":  {"type": "T", "bw": 2000, "As": 897.9,  "sel": "6Φ14", "prov": 923.4},
            "B":  {"type": "rect", "bw": 200, "As": 1559.9, "sel": "5Φ20", "prov": 1571},
            "2":  {"type": "T", "bw": 2000, "As": 529.8,  "sel": "5Φ12", "prov": 565.5},
            "C":  {"type": "rect", "bw": 200, "As": 1112.0, "sel": "3Φ22", "prov": 1140.3},
            "3":  {"type": "T", "bw": 2000, "As": 638.9,  "sel": "6Φ12", "prov": 678.6},
        }

        moments = [
            ("1", 79.2364), ("B", -92.8654), ("2", 47.1374),
            ("C", -75.9268), ("3", 56.7055),
        ]

        for name, M in moments:
            r = ref[name]
            result = calc_beam_flexure(
                name=name, moment=M,
                section_type=r["type"],
                b=200, bf=2000, h=400, hf=80,
                cover=30, bar_diameter=20,
                fc=9.6, fy=300, gamma_d=1.20,
            )
            assert result.as_required == pytest.approx(r["As"], abs=1.0)
            assert len(result.candidates) > 0
            assert result.selected_bar is not None


class TestBeamShear:
    """次梁斜截面箍筋计算"""

    def test_shear_stirrup_against_reference(self):
        """Vmax=74.6237, Vc=46.2, Asv/s=0.446"""
        from app.solvers.beam.utils import calc_beam_shear

        result = calc_beam_shear(
            max_shear=74.6237,
            b=200, h=400, cover=30, bar_diameter=20,
            ft=1.10, fy=300, gamma_d=1.20,
            stirrup_diameter=6, stirrup_legs=2,
            fyv=270,
        )

        assert result.max_shear == pytest.approx(74.62, abs=0.01)
        assert result.asv_s > 0
        assert result.recommended_spacing > 0


class TestBeamLoad:
    """次梁荷载计算"""

    def test_load_against_reference(self):
        """参考网站: 板传5.81, 自重1.6, 粉刷0.1632, gk=7.5732, g=7.9519, q=9.6"""
        from app.solvers.beam.solver import calculate_beam_load

        inp = BeamInput(
            span=7.2,
            slab_dead_load_standard=2.91,  # kN/m²
            live_load_per_area=4.0,  # kN/m²
            beam_spacing=2.0,  # m
            beam_width=200,  # mm
            beam_height=400,  # mm
            slab_thickness=80,  # mm
            concrete_weight=25.0,  # kN/m³
            plaster_thickness=15,  # mm
            plaster_weight=17.0,  # kN/m³
            dead_load_factor=1.05,
            live_load_factor=1.20,
        )

        result = calculate_beam_load(inp)

        assert result.from_slab_dead == pytest.approx(5.82, abs=0.02)
        assert result.self_weight == pytest.approx(1.6, abs=0.01)
        assert result.plaster == pytest.approx(0.1632, abs=0.001)
        assert result.dead_load_standard == pytest.approx(7.58, abs=0.02)
        assert result.dead_load_design == pytest.approx(7.96, abs=0.02)
        assert result.live_load_standard == pytest.approx(8.0, abs=0.01)
        assert result.live_load_design == pytest.approx(9.6, abs=0.01)


class TestBeamConvertedLoad:
    """次梁荷载折算（与板不同：g'=g+q/4, q'=3q/4）"""

    def test_converted_loads(self):
        """参考网站: g'=10.3519, q'=7.2"""
        from app.solvers.beam.solver import convert_beam_loads

        load = BeamLoadOutput(
            from_slab_dead=5.82,
            self_weight=1.6,
            plaster=0.1632,
            dead_load_standard=7.5832,
            dead_load_design=7.9624,
            live_load_standard=8.0,
            live_load_design=9.6,
        )

        result = convert_beam_loads(load)

        assert result.converted_dead == pytest.approx(10.36, abs=0.02)
        assert result.converted_live == pytest.approx(7.2, abs=0.01)


class TestBeamSpan:
    """次梁跨度计算"""

    def test_spans(self):
        """次梁跨度: l₀=7.2m for all"""
        from app.solvers.beam.solver import calculate_beam_spans, calculate_beam_net_spans

        inp = BeamInput(
            slab_dead_load_standard=2.91,
            live_load_per_area=4.0,
            beam_spacing=2.0,
            beam_width=200,
            beam_height=400,
            slab_thickness=80,
            concrete_weight=25.0,
            plaster_thickness=15,
            plaster_weight=17.0,
            dead_load_factor=1.05,
            live_load_factor=1.20,
            support_width=250,  # 主梁宽 (mm)
            span=7.2,  # 跨长 (m)
            wall_thickness=370,  # 墙体厚度 (mm)
            bearing_length=240,  # 搁置长度 (mm)
        )

        spans = calculate_beam_spans(inp)
        net_spans = calculate_beam_net_spans(inp)

        assert spans.middle_span == pytest.approx(7.2, abs=0.01)
        assert spans.edge_span == pytest.approx(7.2, abs=0.01)
        assert net_spans.middle_net == pytest.approx(6.95, abs=0.01)
        assert net_spans.edge_net == pytest.approx(6.95, abs=0.01)


class TestBeamInternalForce:
    """次梁内力计算"""

    @pytest.fixture
    def basic_setup(self):
        """参考网站的荷载与跨度数据"""
        from app.solvers.beam.solver import (
            calculate_beam_load,
            calculate_beam_spans,
            calculate_beam_net_spans,
            convert_beam_loads,
        )

        inp = BeamInput(
            slab_dead_load_standard=2.91,
            live_load_per_area=4.0,
            beam_spacing=2.0,
            beam_width=200,
            beam_height=400,
            slab_thickness=80,
            concrete_weight=25.0,
            plaster_thickness=15,
            plaster_weight=17.0,
            dead_load_factor=1.05,
            live_load_factor=1.20,
            support_width=250,
            span=7.2,
            spans=5,
        )

        load = calculate_beam_load(inp)
        spans = calculate_beam_spans(inp)
        net_spans = calculate_beam_net_spans(inp)
        converted = convert_beam_loads(load)
        return inp, load, spans, net_spans, converted

    def test_internal_force_structure(self, basic_setup):
        """内力结果应有正确的截面数量"""
        from app.solvers.beam.solver import calculate_beam_internal_forces

        inp, load, spans, net_spans, converted = basic_setup
        result = calculate_beam_internal_forces(inp, load, spans, net_spans, converted)

        assert len(result.moments) == 2 * inp.spans - 1  # 9 for 5 spans
        assert len(result.shears) == 2 * inp.spans  # 10 for 5 spans

    def test_moment_m1_positive(self, basic_setup):
        """边跨跨中 M1 应为正 (下侧受拉)"""
        from app.solvers.beam.solver import calculate_beam_internal_forces

        inp, load, spans, net_spans, converted = basic_setup
        result = calculate_beam_internal_forces(inp, load, spans, net_spans, converted)

        m1 = result.moments[0]
        assert m1.name == "M1"
        assert m1.value > 0

    def test_shear_symmetry(self, basic_setup):
        """端支座剪力应对称"""
        from app.solvers.beam.solver import calculate_beam_internal_forces

        inp, load, spans, net_spans, converted = basic_setup
        result = calculate_beam_internal_forces(inp, load, spans, net_spans, converted)

        assert result.shears[0].value == pytest.approx(-result.shears[-1].value, abs=0.01)
