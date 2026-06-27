"""板配筋计算 — 测试"""
import math

import pytest

from app.models.slab import (
    ReinforcementBar,
    SectionReinforcement,
    SlabReinforcementOutput,
)


class TestReinforcementBar:
    """钢筋规格模型"""

    def test_area_per_meter(self):
        """Φ8@200 每米面积 = π×8²/4 × (1000/200) = 251.3"""
        bar = ReinforcementBar(diameter=8, spacing=200)
        expected = math.pi * 8**2 / 4 * (1000 / 200)
        assert bar.area_per_meter == pytest.approx(expected, rel=1e-4)

    def test_display_name(self):
        """显示名称应为 Φ8@200"""
        bar = ReinforcementBar(diameter=8, spacing=200)
        assert bar.display == "Φ8@200"


class TestRebarCandidates:
    """配筋候选方案生成"""

    def test_generate_candidates_basic(self):
        """As=200mm² 时应返回 Φ8@200 (面积 251.3 ≥ 200)"""
        from app.solvers.slab.utils import generate_rebar_candidates

        candidates = generate_rebar_candidates(as_required=200.0)
        names = [c.display for c in candidates]
        assert "Φ8@200" in names
        # 每个方案面积都应 ≥ 200
        for c in candidates:
            assert c.area_per_meter >= 200.0

    def test_generate_candidates_all_meet_requirement(self):
        """每个候选方案的面积应 ≥ As_required"""
        from app.solvers.slab.utils import generate_rebar_candidates

        candidates = generate_rebar_candidates(as_required=300.0)
        for c in candidates:
            assert c.area_per_meter >= 300.0

    def test_generate_candidates_different_requirements(self):
        """As 不同时应返回不同候选列表（更严格的筛选更少候选）"""
        from app.solvers.slab.utils import generate_rebar_candidates

        loose = generate_rebar_candidates(as_required=100.0)
        strict = generate_rebar_candidates(as_required=400.0)
        assert len(loose) > len(strict)


class TestH0Calculation:
    """有效高度 h₀ 计算"""

    def test_h0_with_standard_params(self):
        """h=80, c=20, d=10 → h₀ = 80 - 20 - 10/2 = 55"""
        from app.solvers.common import effective_depth as calc_effective_depth

        result = calc_effective_depth(h=80, cover=20, bar_diameter=10)
        assert result == 55.0


class TestSectionReinforcement:
    """单个截面的配筋计算核心逻辑"""

    def test_alpha_s_calculation(self):
        """αs = γd·M / (fc·b·h₀²) — 用参考网站 M1 的数值"""
        from app.solvers.common import alpha_s as calc_alpha_s

        result = calc_alpha_s(
            moment=2.6627,  # kN·m
            fc=9.6,  # N/mm²
            b=1000,  # mm
            h0=55,  # mm
            gamma_d=1.20,
        )
        assert result == pytest.approx(0.11, abs=0.001)

    def test_xi_calculation(self):
        """ξ = 1 - √(1 - 2αs)"""
        from app.solvers.common import xi as calc_xi

        result = calc_xi(alpha_s=0.11)
        assert result == pytest.approx(0.1169, abs=0.0001)

    def test_as_required_calculation(self):
        """As = ξ·fc/fy·b·h₀"""
        from app.solvers.common import as_required as calc_as_required

        result = calc_as_required(xi=0.1169, fc=9.6, fy=270, b=1000, h0=55)
        assert result == pytest.approx(228.5, abs=0.5)

    def test_full_calculation_m1(self):
        """完整配筋计算：M1 截面，应与参考一致"""
        from app.solvers.slab.utils import calc_section_reinforcement

        section = calc_section_reinforcement(
            name="1",
            moment=2.6627,
            h=80,
            cover=20,
            bar_diameter=10,
            fc=9.6,
            fy=270,
            gamma_d=1.20,
        )

        assert section.name == "1"
        assert section.alpha_s == pytest.approx(0.11, abs=0.001)
        assert section.xi == pytest.approx(0.1169, abs=0.0001)
        assert section.as_required == pytest.approx(228.5, abs=0.5)
        assert section.h0 == 55.0

    def test_full_calculation_mb(self):
        """完整配筋计算：B 支座截面，应与参考一致"""
        from app.solvers.slab.utils import calc_section_reinforcement

        section = calc_section_reinforcement(
            name="B",
            moment=-3.4315,
            h=80,
            cover=20,
            bar_diameter=10,
            fc=9.6,
            fy=270,
            gamma_d=1.20,
        )

        assert section.alpha_s == pytest.approx(0.1418, abs=0.001)
        assert section.xi == pytest.approx(0.1536, abs=0.0001)
        assert section.as_required == pytest.approx(300.4, abs=0.5)

    def test_auto_bar_selection(self):
        """自动选出面积 ≥ As_required 的配筋方案"""
        from app.solvers.slab.utils import calc_section_reinforcement

        section = calc_section_reinforcement(
            name="1", moment=2.6627, h=80, cover=20, bar_diameter=10,
            fc=9.6, fy=270, gamma_d=1.20,
        )

        # 应有至少一个候选方案
        assert len(section.candidates) > 0
        # 所有候选面积都 ≥ As_required
        for c in section.candidates:
            assert c.area_per_meter >= section.as_required
        # 推荐方案应有 Φ8@200（参考网站的选择）
        recommended_names = [c.display for c in section.candidates]
        assert "Φ8@200" in recommended_names


class TestSlabReinforcement:
    """板全部截面的配筋计算"""

    def test_calculate_all_sections(self):
        """一次性计算所有 5 个截面（参考网站数据）"""
        from app.solvers.slab.solver import calculate_slab_reinforcement

        moments = [
            ("1", 2.6627),
            ("B", -3.4315),
            ("2", 1.4771),
            ("C", -2.7879),
            ("3", 1.8280),
        ]

        result = calculate_slab_reinforcement(
            moments=moments,
            h=80,
            cover=20,
            bar_diameter=10,
            fc=9.6,
            fy=270,
            gamma_d=1.20,
        )

        assert len(result.sections) == 5

        # 验证每个截面的 As_required 与参考一致
        expected = {"1": 228.5, "B": 300.4, "2": 123.2, "C": 240.0, "3": 153.8}
        for s in result.sections:
            assert s.name in expected
            assert s.as_required == pytest.approx(expected[s.name], abs=1.0)
