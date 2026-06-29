"""公共模块 — 钢筋混凝土基本公式与通用工具测试"""
import math

import pytest

from app.solvers.common import (
    alpha_s,
    as_required,
    calc_continuous_beam_internal_forces,
    calc_continuous_beam_internal_forces_detailed,
    calc_shear_design,
    effective_depth,
    flexure_status,
    generate_bar_bundles,
    xi,
)


class TestEffectiveDepth:
    """有效高度 h₀ = h − c − d/2"""

    def test_slab_standard(self):
        """板: h=80, c=20, d=10 → 55"""
        assert effective_depth(h=80, cover=20, bar_diameter=10) == 55.0

    def test_beam_standard(self):
        """次梁: h=400, c=30, d=20 → 360"""
        assert effective_depth(h=400, cover=30, bar_diameter=20) == 360.0

    def test_main_beam(self):
        """主梁: h=500, c=30, d=20 → 460"""
        assert effective_depth(h=500, cover=30, bar_diameter=20) == 460.0


class TestAlphaS:
    """αs = γd·M / (fc·b·h₀²)"""

    def test_slab_m1(self):
        """板 M1: M=2.6627, fc=9.6, b=1000, h0=55, γd=1.2 → 0.11"""
        result = alpha_s(moment=2.6627, fc=9.6, b=1000, h0=55, gamma_d=1.2)
        assert result == pytest.approx(0.11, abs=0.001)

    def test_unit_moment(self):
        """M=1kN·m, fc=9.6, b=1000, h0=100, γd=1.2"""
        result = alpha_s(moment=1.0, fc=9.6, b=1000, h0=100, gamma_d=1.2)
        expected = 1.2 * 1.0 * 1e6 / (9.6 * 1000 * 100**2)
        assert result == pytest.approx(expected)


class TestXi:
    """ξ = 1 − √(1 − 2αs)"""

    def test_known_value(self):
        assert xi(0.11) == pytest.approx(0.1169, abs=0.0001)

    def test_zero(self):
        assert xi(0.0) == 0.0


class TestAsRequired:
    """As = ξ·(fc/fy)·b·h₀"""

    def test_slab_m1(self):
        """ξ=0.1169, fc=9.6, fy=270, b=1000, h0=55 → 228.5"""
        result = as_required(xi=0.1169, fc=9.6, fy=270, b=1000, h0=55)
        assert result == pytest.approx(228.5, abs=0.5)


class TestFlexureStatus:
    """配筋状态判定"""

    def test_recommended(self):
        """实配略大于需要 → 推荐"""
        assert flexure_status(as_req=200, as_prov=251) == "推荐"

    def test_review(self):
        """实配远大于需要（>1.8 倍）→ 建议复核"""
        assert flexure_status(as_req=100, as_prov=251) == "建议复核"

    def test_insufficient(self):
        """实配为 0 → 不足"""
        assert flexure_status(as_req=200, as_prov=0) == "不足"


class TestGenerateBarBundles:
    """梁配筋候选生成"""

    def test_all_meet_requirement(self):
        """每个候选面积 ≥ as_required"""
        candidates = generate_bar_bundles(as_required=900, beam_width=250)
        for c in candidates:
            assert c.area >= 900

    def test_strict_fewer_than_loose(self):
        """要求越高候选越少"""
        loose = generate_bar_bundles(as_required=100, beam_width=200)
        strict = generate_bar_bundles(as_required=1500, beam_width=200)
        assert len(loose) > len(strict)

    def test_sorted_by_area(self):
        """候选按面积升序"""
        candidates = generate_bar_bundles(as_required=500, beam_width=250)
        areas = [c.area for c in candidates]
        assert areas == sorted(areas)


class TestCalcShearDesign:
    """斜截面箍筋"""

    def test_secondary_beam(self):
        """次梁: V=74.62, b=200, h=400, c=30, d=20, fc=9.6"""
        result = calc_shear_design(
            max_shear=74.62, b=200, h=400, cover=30, bar_diameter=20,
            ft=1.10, gamma_d=1.2, stirrup_diameter=6, stirrup_legs=2, fyv=270,
        )
        assert result.max_shear == pytest.approx(74.62, abs=0.01)
        assert result.vc == pytest.approx(46.2, abs=0.5)
        assert result.asv_s > 0
        assert result.recommended_spacing > 0
        assert result.hanger_area == 0.0  # 次梁无吊筋
        assert result.need_stirrups is True

    def test_main_beam_with_hanger(self):
        """主梁: 有吊筋时 hanger_area > 0"""
        result = calc_shear_design(
            max_shear=170.71, b=250, h=500, cover=30, bar_diameter=20,
            ft=1.10, gamma_d=1.2, stirrup_diameter=10, stirrup_legs=2, fyv=270,
            hanger_force=50.0,
        )
        assert result.max_shear == pytest.approx(170.71, abs=0.01)
        assert result.hanger_area > 0


class TestCalcContinuousBeamDetailed:
    """内力详细计算 — 暴露 α/α1/β/β1 与中间量"""

    def test_moment_entries_carry_coefficients(self):
        """5 跨板：M1 的 α/α1/l0 与系数表一致，m_raw = α·g·l0²+α1·q·l0²"""
        moments, _ = calc_continuous_beam_internal_forces_detailed(
            g=5.4975, q=2.4, n=5,
            middle_span=2.0, edge_span=1.92,
            middle_net=1.8, edge_net=1.78,
        )
        m1 = moments[0]
        assert m1.name == "M1"
        assert m1.alpha == 0.0781
        assert m1.alpha1 == 0.100
        assert m1.l0 == 1.92
        assert m1.m_raw == pytest.approx(
            0.0781 * m1.g_l0_sq + 0.100 * m1.q_l0_sq, abs=1e-3
        )
        assert m1.value == m1.m_raw  # 跨中无支座边缘调整

    def test_shear_entries_carry_coefficients(self):
        """V_A 的 β/β1 与系数表一致，V = β·g·ln+β1·q·ln"""
        _, shears = calc_continuous_beam_internal_forces_detailed(
            g=5.4975, q=2.4, n=5,
            middle_span=2.0, edge_span=1.92,
            middle_net=1.8, edge_net=1.78,
        )
        va = shears[0]
        assert va.name == "V_A"
        assert va.beta == 0.394
        assert va.beta1 == 0.447
        assert va.value == pytest.approx(va.beta * va.g_ln + va.beta1 * va.q_ln, abs=1e-3)

    def test_support_delta_in_value_not_mraw(self):
        """支座弯矩：value = m_raw + delta，m_raw 不含 delta"""
        moments, _ = calc_continuous_beam_internal_forces_detailed(
            g=10.362, q=7.2, n=5,
            middle_span=6.0, edge_span=5.88,
            middle_net=5.75, edge_net=5.635,
            support_moment_delta=1.5,
        )
        mb = next(m for m in moments if m.name == "M_B")
        assert mb.value == pytest.approx(mb.m_raw + 1.5, abs=1e-3)

    def test_backward_compat_wrapper(self):
        """旧函数仍返回 (name, value) 元组，值与详细版一致"""
        moments, _ = calc_continuous_beam_internal_forces(
            g=5.4975, q=2.4, n=5,
            middle_span=2.0, edge_span=1.92,
            middle_net=1.8, edge_net=1.78,
        )
        assert moments[0][0] == "M1"
        assert moments[0][1] == pytest.approx(2.468, abs=1e-2)
