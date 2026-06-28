"""教师平台实测数据回归测试。

用第 1 组方案的真实设计参数（L1=30, L2=18, 板厚120, 次梁200×500, 主梁300×600,
柱宽350, 次梁间距2m, 主梁跨6m/3跨, 次梁跨6m/5跨, 板9跨简化为五跨连续板）跑三个
求解器，断言荷载/内力/弯矩与教师平台逐项吻合。

注：斜截面 Vc 的 fc/h₀ 约定（次梁 fc=11、主梁 h0=h−c−d）与求解器不一致且两构件
相互矛盾，属待同学确认项，本文件不断言 Vc，仅断言已确认的荷载与内力。
"""

import pytest

from app.models.beam import BeamInput
from app.models.slab import SlabInput
from app.solvers.beam.solver import calculate_beam
from app.solvers.main_beam.solver import (
    calculate_main_beam_internal_forces,
    calculate_main_beam_load,
)
from app.solvers.slab.solver import calculate_slab


class TestSlabMatchesTeacher:
    """板：宽度方向(width=L2=18)跨度、五跨连续板模型。"""

    def _inp(self):
        return SlabInput(
            length=30.0, width=18.0, thickness=120, support_width=200, spans=9,
            reinforced_concrete_weight=25.0, terrazzo_surface=0.65,
            plaster_thickness=15, plaster_weight=17.0, live_load=4.0,
            dead_load_factor=1.05, live_load_factor=1.2,
        )

    def test_load_and_span(self):
        r = calculate_slab(self._inp(), fc=9.6, fy=270, gamma_d=1.2)
        assert r.load.dead_load_standard == pytest.approx(3.905, abs=0.001)
        assert r.converted.converted_dead == pytest.approx(6.5002, abs=0.001)
        assert r.converted.converted_live == pytest.approx(2.4, abs=0.001)
        assert r.span.middle_span == pytest.approx(2.0, abs=0.001)
        assert r.span.edge_span == pytest.approx(1.94, abs=0.001)
        assert r.net_span.middle_net == pytest.approx(1.8, abs=0.001)
        assert r.net_span.edge_net == pytest.approx(1.78, abs=0.001)

    def test_internal_forces(self):
        r = calculate_slab(self._inp(), fc=9.6, fy=270, gamma_d=1.2)
        m = {x.name: x.value for x in r.internal_forces.moments}
        assert m["M1"] == pytest.approx(2.8139, abs=0.001)
        assert m["M_B"] == pytest.approx(-3.8725, abs=0.001)
        assert m["M2"] == pytest.approx(1.6162, abs=0.001)
        assert m["M_C"] == pytest.approx(-3.1197, abs=0.001)
        assert m["M3"] == pytest.approx(2.022, abs=0.001)
        s = {x.name: x.value for x in r.internal_forces.shears}
        assert s["V_A"] == pytest.approx(6.4683, abs=0.001)
        assert s["Vl_B"] == pytest.approx(-9.7689, abs=0.001)
        assert s["Vr_B"] == pytest.approx(8.7378, abs=0.001)
        assert s["Vl_C"] == pytest.approx(-8.0343, abs=0.001)
        assert s["Vr_C"] == pytest.approx(8.4033, abs=0.001)


class TestBeamMatchesTeacher:
    """次梁：span=6, 200×500, 板厚120, 支座=主梁宽300, 五跨连续梁。"""

    def _inp(self):
        return BeamInput(
            span=6.0, beam_width=200, beam_height=500, slab_thickness=120,
            support_width=300, spans=5, beam_spacing=2.0, bearing_length=240,
            slab_dead_load_standard=3.905, live_load_per_area=4.0,
            concrete_weight=25.0, plaster_thickness=15, plaster_weight=17.0,
            dead_load_factor=1.05, live_load_factor=1.2,
        )

    def test_load(self):
        r = calculate_beam(self._inp(), fc=9.6, fy=300, gamma_d=1.2)
        assert r.load.from_slab_dead == pytest.approx(7.81, abs=0.001)
        assert r.load.self_weight == pytest.approx(1.9, abs=0.001)
        assert r.load.plaster == pytest.approx(0.1938, abs=0.001)
        assert r.load.dead_load_standard == pytest.approx(9.9038, abs=0.001)
        assert r.load.dead_load_design == pytest.approx(10.399, abs=0.001)
        assert r.converted.converted_dead == pytest.approx(12.799, abs=0.001)
        assert r.converted.converted_live == pytest.approx(7.2, abs=0.001)

    def test_internal_forces(self):
        r = calculate_beam(self._inp(), fc=9.6, fy=300, gamma_d=1.2)
        m = {x.name: x.value for x in r.internal_forces.moments}
        assert m["M1"] == pytest.approx(61.9056, abs=0.002)
        assert m["M_B"] == pytest.approx(-70.2254, abs=0.002)
        assert m["M2"] == pytest.approx(35.6503, abs=0.002)
        assert m["M_C"] == pytest.approx(-56.172, abs=0.002)
        assert m["M3"] == pytest.approx(43.4489, abs=0.002)
        s = {x.name: x.value for x in r.internal_forces.shears}
        assert s["V_A"] == pytest.approx(47.3367, abs=0.002)
        assert s["Vl_B"] == pytest.approx(-69.6551, abs=0.002)
        assert s["Vr_B"] == pytest.approx(62.9159, abs=0.002)


class TestMainBeamMatchesTeacher:
    """主梁：荷载分量取教师推导值；内力 M1/M2/M_B 与教师吻合。"""

    def test_load_components(self):
        # 问题 5/6/7 的修正推导：次梁恒载 gk×span、自重扣板厚腹板、活载从属面积
        r = calculate_main_beam_load(
            from_beam_dead=59.4228, self_weight=7.2, plaster=0.4896,
            live_load=48.0, dead_load_factor=1.05, live_load_factor=1.20,
        )
        assert r.dead_load_standard == pytest.approx(67.1124, abs=0.001)
        assert r.dead_load_design == pytest.approx(70.468, abs=0.001)
        assert r.live_load_standard == pytest.approx(48.0, abs=0.001)
        assert r.live_load_design == pytest.approx(57.6, abs=0.001)

    def test_internal_forces(self):
        r = calculate_main_beam_internal_forces(
            dead_load=70.468, live_load=57.6, span=6.0, support_width=350,
        )
        assert r.M1_max == pytest.approx(203.0436, abs=0.002)   # 边跨轴线 6.0
        assert r.M2_max == pytest.approx(96.36, abs=0.01)        # 中跨 1.05×ln=5.933
        assert r.M_B_min == pytest.approx(-206.6862, abs=0.002)  # 支座 5.933 + V₀调整
        assert r.VA_max == pytest.approx(101.5347, abs=0.002)
        assert r.VBl_min == pytest.approx(-164.7966, abs=0.002)
        assert r.VBr_max == pytest.approx(140.8552, abs=0.002)
