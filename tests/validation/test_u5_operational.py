"""Tests derived from SPEC acceptance criteria for U5: Operationality validation.

AC1: Missing acceptance_criteria → error-severity issue in report, is_operational False.
     validate_operational() does NOT raise (edge case takes precedence over AC1 wording).
AC2: All five PM-section components populated → is_operational() returns True.
Edge cases per spec:
  - Empty acceptance_criteria: error, no raise.
  - Acceptance criterion with no input_pattern: warning, included as skipped stub.
  - Soft dependency with unresolved target: info, not warning.
"""

import pytest

from sddkit.models.components import (
    AcceptanceCriterion,
    Constraint,
    Dependency,
    Intent,
    NonGoal,
    ValidationReport,
)
from sddkit.models.spec import Spec
from sddkit.validation.operational import validate_spec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_spec(**kwargs: object) -> Spec:
    defaults: dict = dict(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example intent"),
    )
    defaults.update(kwargs)
    return Spec(**defaults)


def _full_operational_spec() -> Spec:
    """Spec with all five PM-section components populated."""
    return Spec(
        name="full",
        identifier="full/v1",
        version="1.0.0",
        status="active",
        intent=Intent(summary="Full intent", details="Details here"),
        constraints=[Constraint(id="C1", text="Must be fast")],
        acceptance_criteria=[
            AcceptanceCriterion(id="AC1", text="Does the thing", input_pattern="x")
        ],
        non_goals=[NonGoal(id="NG1", text="Not a web UI")],
        dependencies=[Dependency(name="pydantic")],
    )


def _errors(report: ValidationReport) -> list[str]:
    return [i.component for i in report.issues if i.severity == "error"]


def _warnings(report: ValidationReport) -> list[str]:
    return [i.component for i in report.issues if i.severity == "warning"]


# ---------------------------------------------------------------------------
# AC1: missing acceptance_criteria → error, no raise
# ---------------------------------------------------------------------------


def test_ac1_empty_acceptance_criteria_reports_error() -> None:
    spec = _minimal_spec(acceptance_criteria=[])
    report = spec.validate_operational()
    assert "acceptance_criteria" in _errors(report)


def test_ac1_empty_acceptance_criteria_is_not_operational() -> None:
    spec = _minimal_spec(acceptance_criteria=[])
    assert spec.is_operational() is False


def test_ac1_validate_operational_does_not_raise() -> None:
    # Edge case: validate_operational() reports error, does NOT raise.
    spec = _minimal_spec(acceptance_criteria=[])
    report = spec.validate_operational()  # must not raise
    assert isinstance(report, ValidationReport)


def test_ac1_error_message_names_missing_component() -> None:
    spec = _minimal_spec(acceptance_criteria=[])
    report = spec.validate_operational()
    error_issues = [i for i in report.issues if i.severity == "error"]
    assert any("acceptance_criteria" in i.component for i in error_issues)


# ---------------------------------------------------------------------------
# AC2: all five PM-section components populated → is_operational True
# ---------------------------------------------------------------------------


def test_ac2_all_five_components_populated_is_operational() -> None:
    assert _full_operational_spec().is_operational() is True


def test_ac2_all_five_components_no_error_issues() -> None:
    report = _full_operational_spec().validate_operational()
    assert _errors(report) == []


def test_ac2_validate_operational_returns_validation_report() -> None:
    report = _full_operational_spec().validate_operational()
    assert isinstance(report, ValidationReport)
    assert report.is_operational is True


# ---------------------------------------------------------------------------
# Validation logic: name and intent
# ---------------------------------------------------------------------------


def test_empty_name_reports_error() -> None:
    spec = _minimal_spec(name="", acceptance_criteria=[AcceptanceCriterion(id="AC1", text="x", input_pattern="y")])
    report = validate_spec(spec)
    assert "name" in _errors(report)


def test_empty_intent_summary_reports_error() -> None:
    spec = _minimal_spec(
        intent=Intent(summary=""),
        acceptance_criteria=[AcceptanceCriterion(id="AC1", text="x", input_pattern="y")],
    )
    report = validate_spec(spec)
    assert "intent" in _errors(report)


# ---------------------------------------------------------------------------
# Validation logic: warnings for missing optional PM components
# ---------------------------------------------------------------------------


def test_empty_constraints_reports_warning() -> None:
    spec = _minimal_spec(
        constraints=[],
        acceptance_criteria=[AcceptanceCriterion(id="AC1", text="x", input_pattern="y")],
    )
    report = validate_spec(spec)
    assert "constraints" in _warnings(report)
    assert report.is_operational is True  # warnings don't block operationality


def test_empty_non_goals_reports_warning() -> None:
    spec = _minimal_spec(
        non_goals=[],
        acceptance_criteria=[AcceptanceCriterion(id="AC1", text="x", input_pattern="y")],
    )
    report = validate_spec(spec)
    assert "non_goals" in _warnings(report)
    assert report.is_operational is True


# ---------------------------------------------------------------------------
# Edge case: AC with no input_pattern → warning, not error
# ---------------------------------------------------------------------------


def test_ac_without_input_pattern_reports_warning() -> None:
    spec = _minimal_spec(
        acceptance_criteria=[AcceptanceCriterion(id="AC1", text="Does thing")],
        # input_pattern is None (default)
    )
    report = validate_spec(spec)
    warning_components = [i.component for i in report.issues if i.severity == "warning"]
    assert any("AC1" in c for c in warning_components)


def test_ac_without_input_pattern_still_operational_if_no_errors() -> None:
    spec = Spec(
        name="s",
        identifier="s/v1",
        version="1.0",
        status="active",
        intent=Intent(summary="x"),
        constraints=[Constraint(text="must do x")],
        acceptance_criteria=[AcceptanceCriterion(id="AC1", text="Does x")],
        non_goals=[NonGoal(text="Not y")],
        dependencies=[Dependency(name="pydantic")],
    )
    assert spec.is_operational() is True


# ---------------------------------------------------------------------------
# Edge case: soft dependency → info severity (not warning)
# ---------------------------------------------------------------------------


def test_soft_dependency_not_warning() -> None:
    spec = _minimal_spec(
        acceptance_criteria=[AcceptanceCriterion(id="AC1", text="x", input_pattern="y")],
        dependencies=[Dependency(name="optional-lib", kind="soft")],
    )
    report = validate_spec(spec)
    dep_issues = [i for i in report.issues if "dependenc" in i.component.lower()]
    # A soft dependency present means the list is non-empty — no info issue expected
    assert all(i.severity != "warning" for i in dep_issues)


# ---------------------------------------------------------------------------
# is_operational is consistent with validate_operational
# ---------------------------------------------------------------------------


def test_is_operational_consistent_with_report() -> None:
    for ac_list in ([], [AcceptanceCriterion(id="AC1", text="x", input_pattern="y")]):
        spec = _minimal_spec(acceptance_criteria=ac_list)
        report = spec.validate_operational()
        assert spec.is_operational() == report.is_operational


# ---------------------------------------------------------------------------
# Multiple errors reported together
# ---------------------------------------------------------------------------


def test_multiple_errors_all_reported() -> None:
    spec = _minimal_spec(name="", acceptance_criteria=[])
    report = validate_spec(spec)
    error_components = _errors(report)
    assert "name" in error_components
    assert "acceptance_criteria" in error_components
