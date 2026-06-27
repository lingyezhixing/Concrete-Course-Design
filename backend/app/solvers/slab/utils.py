"""连续梁系数查表 — 多跨简支板的弯矩与剪力系数"""

from dataclasses import dataclass

__all__ = ["SlabCoefficients", "get_slab_coefficients"]


@dataclass
class Coeff:
    """单个位置的系数组"""
    alpha: float   # 恒荷载弯矩系数
    alpha1: float  # 活荷载弯矩系数
    beta: float    # 恒荷载剪力系数
    beta1: float   # 活荷载剪力系数


@dataclass
class SlabCoefficients:
    """某跨数连续梁的完整系数集合"""
    spans: int
    moments: list[float]   # 弯矩系数 [跨1中, 支座B, 跨2中, 支座C, ...]
    shears: list[float]    # 剪力系数 [端支座A, 支座B左, 支座B右, ...]
    moment_alpha1: list[float]   # 活荷载弯矩系数
    shear_beta1: list[float]     # 活荷载剪力系数


# ============================================================
# 系数表：(弯矩α, 弯矩α1, 剪力β, 剪力β1)
# 弯矩按：跨1中, 支座B, 跨2中, 支座C, ... 顺序
# 剪力按：端支座A, 支座B左, 支座B右, 支座C左, ... 顺序
# ============================================================

_COEFFICIENTS: dict[int, SlabCoefficients] = {
    2: SlabCoefficients(
        spans=2,
        moments=[0.070, -0.125, 0.070],
        moment_alpha1=[0.096, -0.125, 0.096],
        shears=[0.375, -0.625, 0.625, -0.375],
        shear_beta1=[0.437, -0.625, 0.625, -0.437],
    ),
    3: SlabCoefficients(
        spans=3,
        moments=[0.080, -0.100, 0.025, -0.100, 0.080],
        moment_alpha1=[0.101, -0.117, 0.075, -0.117, 0.101],
        shears=[0.400, -0.600, 0.500, -0.500, 0.600, -0.400],
        shear_beta1=[0.450, -0.617, 0.583, -0.583, 0.617, -0.450],
    ),
    4: SlabCoefficients(
        spans=4,
        moments=[0.077, -0.107, 0.036, -0.071, 0.036, -0.107, 0.077],
        moment_alpha1=[0.100, -0.121, 0.081, -0.107, 0.081, -0.121, 0.100],
        shears=[0.393, -0.607, 0.536, -0.464, 0.464, -0.536, 0.607, -0.393],
        shear_beta1=[0.446, -0.620, 0.603, -0.571, 0.517, -0.603, 0.620, -0.446],
    ),
    5: SlabCoefficients(
        spans=5,
        moments=[0.0781, -0.105, 0.0331, -0.079, 0.0462, -0.079, 0.0331, -0.105, 0.0781],
        moment_alpha1=[0.100, -0.119, 0.0787, -0.111, 0.0855, -0.111, 0.0787, -0.119, 0.100],
        shears=[0.394, -0.606, 0.526, -0.474, 0.500, -0.500, 0.474, -0.526, 0.606, -0.394],
        shear_beta1=[0.447, -0.620, 0.598, -0.576, 0.591, -0.591, 0.576, -0.598, 0.620, -0.447],
    ),
}


def get_slab_coefficients(spans: int) -> SlabCoefficients:
    """根据跨数获取连续梁系数。

    Args:
        spans: 跨数，支持 2 ~ 5

    Returns:
        SlabCoefficients 数据对象

    Raises:
        ValueError: 跨数不在支持范围内
    """
    if spans not in _COEFFICIENTS:
        raise ValueError(f"不支持 {spans} 跨，目前仅支持 2 ~ 5 跨")
    return _COEFFICIENTS[spans]
