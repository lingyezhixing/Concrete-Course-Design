"""主梁计算 — 测试"""
import math
import pytest


class TestMainBeamLoad:
    """主梁荷载计算（集中力）"""

    def test_load_against_reference(self):
        """教师示例: Gk=67.1124, G=70.468; Qk=48.0, Q=57.6
        （荷载分量取问题 5/6/7 的修正推导值：次梁恒载 g_std×span、
          自重扣板厚腹板、活载按从属面积）"""
        from app.solvers.main_beam.solver import calculate_main_beam_load

        result = calculate_main_beam_load(
            from_beam_dead=59.4228,
            self_weight=7.2,
            plaster=0.4896,
            live_load=48.0,
            dead_load_factor=1.05,
            live_load_factor=1.20,
        )

        assert result.dead_load_standard == pytest.approx(67.1124, abs=0.01)
        assert result.dead_load_design == pytest.approx(70.468, abs=0.01)
        assert result.live_load_standard == pytest.approx(48.0, abs=0.01)
        assert result.live_load_design == pytest.approx(57.6, abs=0.01)


class TestMainBeamCoefficients:
    """三等跨连续梁三等分集中荷载系数表"""

    def test_coefficients_exist(self):
        """系数表应包含所有截面"""
        from app.solvers.main_beam.utils import get_main_beam_coefficients

        coeffs = get_main_beam_coefficients()
        assert "M1" in coeffs
        assert "M_B" in coeffs
        assert "VA" in coeffs
        assert "VBl" in coeffs

    def test_coefficient_values(self):
        """验证几个关键系数"""
        from app.solvers.main_beam.utils import get_main_beam_coefficients

        c = get_main_beam_coefficients()
        # Row 1: G on all spans
        assert c["M1"]["G_all"] == 0.244
        assert c["M_B"]["G_all"] == -0.267
        assert c["VA"]["G_all"] == 0.733
        # Row 2: Q on spans 1,3
        assert c["M1"]["Q_13"] == 0.289
        assert c["VA"]["Q_13"] == 0.866


class TestMainBeamInternalForce:
    """主梁内力计算"""

    def test_midspan_moments(self):
        """M1, M2 应与教师示例一致：M1 边跨用轴线 6.0，M2 中跨用 5.933"""
        from app.solvers.main_beam.solver import calculate_main_beam_internal_forces

        result = calculate_main_beam_internal_forces(
            dead_load=70.468,
            live_load=57.6,
            span=6.0,
            support_width=350,
        )

        # M1 = (0.244·70.468 + 0.289·57.6) × 6.0（边跨轴线）= 203.0436
        assert result.M1_max == pytest.approx(203.04, abs=0.1)
        # M2 = (0.067·70.468 + 0.200·57.6) × 5.9325（中跨 1.05×ln）= 96.3518
        assert result.M2_max == pytest.approx(96.36, abs=0.05)

    def test_support_shears(self):
        """支座剪力应与教师示例一致（剪力与跨度无关）"""
        from app.solvers.main_beam.solver import calculate_main_beam_internal_forces

        result = calculate_main_beam_internal_forces(
            dead_load=70.468,
            live_load=57.6,
            span=6.0,
            support_width=350,
        )

        # VA = 0.733·70.468 + 0.866·57.6 = 101.53
        assert result.VA_max == pytest.approx(101.53, abs=0.1)
        # VBl = -1.267·70.468 - 1.311·57.6 = -164.80
        assert result.VBl_min == pytest.approx(-164.80, abs=0.1)
        # VBr = 1.000·70.468 + 1.222·57.6 = 140.86
        assert result.VBr_max == pytest.approx(140.86, abs=0.1)

    def test_support_moment_adjusted(self):
        """M_B/M_C 支座边缘调整：支座用 L2=1.05×(轴线−柱宽)，V₀=(G+Q)/2 简支剪力"""
        from app.solvers.main_beam.solver import calculate_main_beam_internal_forces

        result = calculate_main_beam_internal_forces(
            dead_load=70.468,
            live_load=57.6,
            span=6.0,
            support_width=350,
        )

        # L2 = 1.05×(6.0−0.35) = 5.9325；V₀ = (70.468+57.6)/2 = 64.034
        # M_B = (-0.267·70.468 - 0.311·57.6) × 5.9325 + (0.35/2)·64.034 = -206.69
        assert result.M_B_min == pytest.approx(-206.69, abs=0.5)
        # M_C = (-0.267·70.468 - 0.089·57.6) × 5.9325 + (0.35/2)·64.034 = -130.83
        assert result.M_C_min == pytest.approx(-130.83, abs=0.5)

    def test_envelope_has_all_fields(self):
        """包络结果应包含完整字段"""
        from app.solvers.main_beam.solver import calculate_main_beam_internal_forces

        result = calculate_main_beam_internal_forces(
            dead_load=70.468,
            live_load=57.6,
            span=6.0,
            support_width=350,
        )

        assert result.M1_max is not None
        assert result.M2_max is not None
        assert result.M_B_min is not None
        assert result.VA_max is not None
        assert result.VBl_min is not None
        assert result.VBr_max is not None


class TestMainBeamFlexure:
    """主梁正截面配筋（T形）"""

    def test_section_1(self):
        """M1=212.40, T形bf=2000 → As=1908.9, 选4Φ25"""
        from app.solvers.main_beam.utils import calc_main_beam_flexure

        result = calc_main_beam_flexure(
            name="1",
            moment=212.4019,
            h=500, b=250, bf=2000, hf=80,
            cover=30, bar_diameter=20,
            fc=9.6, fy=300, gamma_d=1.20,
        )

        assert result.as_required == pytest.approx(1908.9, abs=1.0)
        sel = result.selected_bar
        assert sel is not None and "4Φ25" in result.selected_bar.display

    def test_section_b(self):
        """M_B=218.67, T形(课程简化)bf=2000 → As=1967.2, 选6Φ22"""
        from app.solvers.main_beam.utils import calc_main_beam_flexure

        result = calc_main_beam_flexure(
            name="B",
            moment=218.6701,
            h=500, b=250, bf=2000, hf=80,
            cover=30, bar_diameter=20,
            fc=9.6, fy=300, gamma_d=1.20,
            use_t_section=True,  # 课程简化：支座也按T形
        )

        assert result.as_required == pytest.approx(1967.2, abs=1.0)

    def test_section_2(self):
        """M2=108.36, T形bf=2000 → As=957.8, 选2Φ25"""
        from app.solvers.main_beam.utils import calc_main_beam_flexure

        result = calc_main_beam_flexure(
            name="2",
            moment=108.3567,
            h=500, b=250, bf=2000, hf=80,
            cover=30, bar_diameter=20,
            fc=9.6, fy=300, gamma_d=1.20,
        )

        assert result.as_required == pytest.approx(957.8, abs=1.0)


class TestMainBeamShear:
    """主梁斜截面箍筋与吊筋"""

    def test_stirrup(self):
        """最大剪力170.71kN → Vc=63.25kN"""
        from app.solvers.main_beam.utils import calc_main_beam_shear

        result = calc_main_beam_shear(
            max_shear=170.7106,
            b=250, h=500, cover=30, bar_diameter=20,
            fc=9.6, gamma_d=1.20,
            stirrup_diameter=10, stirrup_legs=2,
            fyv=270,
        )

        assert result.max_shear == pytest.approx(170.71, abs=0.01)
        assert result.asv_s > 0
        assert result.recommended_spacing > 0


class TestMainBeamOrchestration:
    """主梁完整编排 calculate_main_beam（Task 9 荷载推导 + 内力 + 配筋 + 吊筋）。

    用第1组方案 A 参数（主梁300×600、板厚120、次梁间距2m、跨度6m），
    校核荷载分量、内力、吊筋与教师示例一致。
    """

    def test_load_components_match_teacher(self):
        """集中力分量：次梁恒载59.4228 / 自重7.2 / 粉刷0.4896 / 活载48"""
        from app.models.main_beam import MainBeamInput
        from app.solvers.main_beam.solver import calculate_main_beam

        inp = MainBeamInput(
            span=6.0, beam_width=300, beam_height=600, slab_thickness=120,
            column_width=350, spans=3, beam_spacing=2.0,
            from_beam_dead=59.4228, self_weight=7.2, plaster=0.4896, live_load=48.0,
        )
        result = calculate_main_beam(inp, fc=9.6, fy=300, gamma_d=1.2)
        assert result.load.dead_load_standard == pytest.approx(67.1124, abs=0.001)
        assert result.load.dead_load_design == pytest.approx(70.468, abs=0.001)
        assert result.load.live_load_design == pytest.approx(57.6, abs=0.001)

    def test_internal_and_hanger_match_teacher(self):
        """M1=203.04 / M2=96.36 / M_B=-206.69；吊筋面积≈754.2"""
        from app.models.main_beam import MainBeamInput
        from app.solvers.main_beam.solver import calculate_main_beam

        inp = MainBeamInput(
            span=6.0, beam_width=300, beam_height=600, slab_thickness=120,
            column_width=350, spans=3, beam_spacing=2.0,
            from_beam_dead=59.4228, self_weight=7.2, plaster=0.4896, live_load=48.0,
        )
        result = calculate_main_beam(inp, fc=9.6, fy=300, gamma_d=1.2)
        # 内力在 reinforcement 内部计算
        m1 = result.reinforcement.flexure[0]
        mb = result.reinforcement.flexure[1]
        m2 = result.reinforcement.flexure[2]
        assert m1.moment == pytest.approx(203.0436, abs=0.01)
        assert mb.moment == pytest.approx(206.6862, abs=0.01)  # 取绝对值
        assert m2.moment == pytest.approx(96.36, abs=0.01)
        # 吊筋：F=from_beam_dead×1.05+live×1.2≈120 → Asb≈754.2
        assert result.reinforcement.shear.hanger_area == pytest.approx(754.2, abs=1.0)

