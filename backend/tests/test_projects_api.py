"""项目 CRUD 端点测试（隔离、has_uncommitted、门禁）。"""

from app.models.project import (
    MATERIALS_REQUIRED,
    ProjectCreate,
    ProjectPatch,
    SLAB_REQUIRED_INPUT,
)


def test_project_create_validates_name():
    from pydantic import ValidationError

    ProjectCreate(name="p1")  # ok
    try:
        ProjectCreate(name="")
        raise AssertionError("空名应拒绝")
    except ValidationError:
        pass


def test_required_field_constants():
    assert "length" in SLAB_REQUIRED_INPUT and "thickness" in SLAB_REQUIRED_INPUT
    # 有默认值的字段不计入必需
    assert "dead_load_factor" not in SLAB_REQUIRED_INPUT
    assert {"fc", "fy_slab", "gamma_d"} <= set(MATERIALS_REQUIRED)


def test_project_patch_all_optional():
    p = ProjectPatch()
    assert p.name is None and p.data is None
    p2 = ProjectPatch(name="x")
    assert p2.name == "x"
