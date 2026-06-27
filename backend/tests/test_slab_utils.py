"""连续梁系数查表测试（板、次梁共用）"""

import pytest
from app.solvers.common import get_continuous_beam_coefficients, ContinuousBeamCoefficients


class TestGetContinuousBeamCoefficients:
    """get_continuous_beam_coefficients 基础行为"""

    def test_returns_correct_type(self):
        coeffs = get_continuous_beam_coefficients(2)
        assert isinstance(coeffs, ContinuousBeamCoefficients)

    def test_unsupported_spans_raises(self):
        with pytest.raises(ValueError, match="不支持"):
            get_continuous_beam_coefficients(1)
        with pytest.raises(ValueError, match="不支持"):
            get_continuous_beam_coefficients(6)

    def test_supported_range(self):
        """2 ~ 5 跨均不应报错"""
        for spans in (2, 3, 4, 5):
            coeffs = get_continuous_beam_coefficients(spans)
            assert coeffs.spans == spans


class TestTwoSpanCoefficients:
    """双跨梁系数验证"""

    @pytest.fixture
    def coeffs(self):
        return get_continuous_beam_coefficients(2)

    def test_moment_count(self, coeffs):
        """3 个弯矩位置：跨1中、支座B、跨2中"""
        assert len(coeffs.moments) == 3
        assert len(coeffs.moment_alpha1) == 3

    def test_shear_count(self, coeffs):
        """4 个剪力位置：端A、B左、B右、端C"""
        assert len(coeffs.shears) == 4
        assert len(coeffs.shear_beta1) == 4

    def test_moment_values(self, coeffs):
        assert coeffs.moments == [0.070, -0.125, 0.070]
        assert coeffs.moment_alpha1 == [0.096, -0.125, 0.096]

    def test_shear_values(self, coeffs):
        assert coeffs.shears == [0.375, -0.625, 0.625, -0.375]
        assert coeffs.shear_beta1 == [0.437, -0.625, 0.625, -0.437]

    def test_symmetry_moment(self, coeffs):
        """弯矩系数应对称"""
        assert coeffs.moments[0] == coeffs.moments[-1]
        assert coeffs.moment_alpha1[0] == coeffs.moment_alpha1[-1]

    def test_symmetry_shear(self, coeffs):
        """剪力系数应对称（符号相反）"""
        assert coeffs.shears[0] == -coeffs.shears[-1]
        assert coeffs.shear_beta1[0] == -coeffs.shear_beta1[-1]


class TestThreeSpanCoefficients:
    """三跨梁系数验证"""

    @pytest.fixture
    def coeffs(self):
        return get_continuous_beam_coefficients(3)

    def test_moment_count(self, coeffs):
        """5 个弯矩位置：跨1中、B、跨2中、C、跨3中"""
        assert len(coeffs.moments) == 5
        assert len(coeffs.moment_alpha1) == 5

    def test_shear_count(self, coeffs):
        """6 个剪力位置：A、B左、B右、C左、C右、D"""
        assert len(coeffs.shears) == 6
        assert len(coeffs.shear_beta1) == 6

    def test_moment_values(self, coeffs):
        assert coeffs.moments == [0.080, -0.100, 0.025, -0.100, 0.080]
        assert coeffs.moment_alpha1 == [0.101, -0.117, 0.075, -0.117, 0.101]

    def test_shear_values(self, coeffs):
        assert coeffs.shears == [0.400, -0.600, 0.500, -0.500, 0.600, -0.400]
        assert coeffs.shear_beta1 == [0.450, -0.617, 0.583, -0.583, 0.617, -0.450]


class TestFourSpanCoefficients:
    """四跨梁系数验证"""

    @pytest.fixture
    def coeffs(self):
        return get_continuous_beam_coefficients(4)

    def test_moment_count(self, coeffs):
        assert len(coeffs.moments) == 7
        assert len(coeffs.moment_alpha1) == 7

    def test_shear_count(self, coeffs):
        assert len(coeffs.shears) == 8
        assert len(coeffs.shear_beta1) == 8

    def test_moment_values(self, coeffs):
        assert coeffs.moments == [0.077, -0.107, 0.036, -0.071, 0.036, -0.107, 0.077]
        assert coeffs.moment_alpha1 == [0.100, -0.121, 0.081, -0.107, 0.081, -0.121, 0.100]

    def test_shear_values(self, coeffs):
        assert coeffs.shears == [0.393, -0.607, 0.536, -0.464, 0.464, -0.536, 0.607, -0.393]
        assert coeffs.shear_beta1 == [0.446, -0.620, 0.603, -0.571, 0.517, -0.603, 0.620, -0.446]


class TestFiveSpanCoefficients:
    """五跨梁系数验证"""

    @pytest.fixture
    def coeffs(self):
        return get_continuous_beam_coefficients(5)

    def test_moment_count(self, coeffs):
        assert len(coeffs.moments) == 9
        assert len(coeffs.moment_alpha1) == 9

    def test_shear_count(self, coeffs):
        assert len(coeffs.shears) == 10
        assert len(coeffs.shear_beta1) == 10

    def test_moment_values(self, coeffs):
        assert coeffs.moments == [0.0781, -0.105, 0.0331, -0.079, 0.0462, -0.079, 0.0331, -0.105, 0.0781]
        assert coeffs.moment_alpha1 == [0.100, -0.119, 0.0787, -0.111, 0.0855, -0.111, 0.0787, -0.119, 0.100]

    def test_shear_values(self, coeffs):
        assert coeffs.shears == [0.394, -0.606, 0.526, -0.474, 0.500, -0.500, 0.474, -0.526, 0.606, -0.394]
        assert coeffs.shear_beta1 == [0.447, -0.620, 0.598, -0.576, 0.591, -0.591, 0.576, -0.598, 0.620, -0.447]
