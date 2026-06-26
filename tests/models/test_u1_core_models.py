"""Tests derived from SPEC acceptance criteria for U1: Core models package.

AC9: Package exposes the required public types.
Structural tests: Spec and component models construct, validate types, and
use Pydantic value equality.
"""

import pytest

import sddkit
from sddkit.models.components import (
    AcceptanceCriterion,
    Constraint,
    Dependency,
    Intent,
    Issue,
    NonGoal,
    ValidationReport,
)
from sddkit.models.refinement import EngineerRefinement, Unit
from sddkit.models.spec import Spec


# ---------------------------------------------------------------------------
# AC9: public surface
# ---------------------------------------------------------------------------


def test_ac9_spec_importable_from_package_root() -> None:
    assert hasattr(sddkit, "Spec")


def test_ac9_intent_importable_from_package_root() -> None:
    assert hasattr(sddkit, "Intent")


def test_ac9_constraint_importable_from_package_root() -> None:
    assert hasattr(sddkit, "Constraint")


def test_ac9_acceptance_criterion_importable_from_package_root() -> None:
    assert hasattr(sddkit, "AcceptanceCriterion")


def test_ac9_non_goal_importable_from_package_root() -> None:
    assert hasattr(sddkit, "NonGoal")


def test_ac9_dependency_importable_from_package_root() -> None:
    assert hasattr(sddkit, "Dependency")


def test_ac9_engineer_refinement_importable_from_package_root() -> None:
    assert hasattr(sddkit, "EngineerRefinement")


def test_ac9_unit_importable_from_package_root() -> None:
    assert hasattr(sddkit, "Unit")


def test_ac9_validation_report_importable_from_package_root() -> None:
    assert hasattr(sddkit, "ValidationReport")


# ---------------------------------------------------------------------------
# Structural: Spec construction
# ---------------------------------------------------------------------------


def _minimal_spec() -> Spec:
    return Spec(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example intent"),
    )


def test_spec_constructs_with_required_fields() -> None:
    spec = _minimal_spec()
    assert spec.name == "example"
    assert spec.identifier == "example/v1"
    assert spec.version == "1.0.0"
    assert spec.status == "draft"


def test_spec_defaults_to_empty_lists() -> None:
    spec = _minimal_spec()
    assert spec.constraints == []
    assert spec.acceptance_criteria == []
    assert spec.non_goals == []
    assert spec.dependencies == []
    assert spec.refinement is None


def test_spec_status_rejects_invalid_value() -> None:
    with pytest.raises(Exception):
        Spec(
            name="x",
            identifier="x/v1",
            version="1.0.0",
            status="unknown",  # type: ignore[arg-type]
            intent=Intent(summary="x"),
        )


def test_spec_missing_name_raises() -> None:
    with pytest.raises(Exception):
        Spec(  # type: ignore[call-arg]
            identifier="x/v1",
            version="1.0.0",
            status="draft",
            intent=Intent(summary="x"),
        )


def test_spec_missing_intent_raises() -> None:
    with pytest.raises(Exception):
        Spec(  # type: ignore[call-arg]
            name="x",
            identifier="x/v1",
            version="1.0.0",
            status="draft",
        )


# ---------------------------------------------------------------------------
# Structural: value equality (invariant)
# ---------------------------------------------------------------------------


def test_spec_value_equality() -> None:
    a = _minimal_spec()
    b = _minimal_spec()
    assert a == b


def test_spec_inequality_on_different_name() -> None:
    a = _minimal_spec()
    b = Spec(
        name="other",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example intent"),
    )
    assert a != b


# ---------------------------------------------------------------------------
# Structural: component models
# ---------------------------------------------------------------------------


def test_intent_constructs() -> None:
    intent = Intent(summary="Do something useful")
    assert intent.summary == "Do something useful"
    assert intent.details == ""


def test_constraint_constructs() -> None:
    c = Constraint(text="Must not use eval")
    assert c.kind == "must"


def test_acceptance_criterion_constructs() -> None:
    ac = AcceptanceCriterion(id="AC1", text="Does the right thing")
    assert ac.input_pattern is None


def test_non_goal_constructs() -> None:
    ng = NonGoal(text="Not a web UI")
    assert ng.id == ""


def test_dependency_constructs() -> None:
    dep = Dependency(name="pydantic")
    assert dep.kind == "hard"


def test_issue_constructs() -> None:
    issue = Issue(severity="error", component="name", message="Missing")
    assert issue.severity == "error"


def test_validation_report_constructs() -> None:
    report = ValidationReport(is_operational=True)
    assert report.issues == []


# ---------------------------------------------------------------------------
# Structural: refinement models
# ---------------------------------------------------------------------------


def test_unit_constructs() -> None:
    u = Unit(id="U1", name="Core models")
    assert u.hard_deps == []
    assert u.soft_deps == []


def test_engineer_refinement_constructs() -> None:
    er = EngineerRefinement(decomposition=[Unit(id="U1", name="Core models")])
    assert len(er.decomposition) == 1


def test_spec_with_refinement() -> None:
    spec = Spec(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="active",
        intent=Intent(summary="Example"),
        refinement=EngineerRefinement(
            decomposition=[Unit(id="U1", name="Core models")]
        ),
    )
    assert spec.refinement is not None
    assert len(spec.refinement.decomposition) == 1


# ---------------------------------------------------------------------------
# Structural: stub methods raise NotImplementedError (not another exception)
# ---------------------------------------------------------------------------


def test_stub_validate_operational_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.validate_operational()


def test_stub_is_operational_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.is_operational()


def test_to_yaml_returns_string() -> None:
    # U3 implemented: to_yaml() now works rather than raising NotImplementedError.
    assert isinstance(_minimal_spec().to_yaml(), str)


def test_to_json_returns_string() -> None:
    # U3 implemented: to_json() now works rather than raising NotImplementedError.
    assert isinstance(_minimal_spec().to_json(), str)


def test_stub_to_markdown_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.to_markdown()


def test_stub_to_agents_md_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.to_agents_md()


def test_stub_emit_skill_file_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.emit_skill_file("spec_ingestion")


def test_stub_decompose_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.decompose()


def test_stub_derive_tests_raises_not_implemented() -> None:
    spec = _minimal_spec()
    with pytest.raises(NotImplementedError):
        spec.derive_tests()
