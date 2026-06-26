"""Operationality validation for Spec.

validate_spec() always returns a ValidationReport — it never raises.
is_operational is True when the report contains no error-severity issues.

The five PM-section components required for full operationality are:
  intent (always present if Spec constructed), constraints, acceptance_criteria,
  non_goals, and dependencies.  Missing acceptance_criteria is the only hard
  error; missing constraints / non_goals / dependencies are warnings.

Spec invariant: AC1 edge case takes precedence over the AC1 wording — the
validator reports rather than raises.  See SPEC.md Edge Cases.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from sddkit.models.components import Issue, ValidationReport

if TYPE_CHECKING:
    from sddkit.models.spec import Spec


def validate_spec(spec: "Spec") -> ValidationReport:
    issues: list[Issue] = []

    if not spec.name.strip():
        issues.append(
            Issue(
                severity="error",
                component="name",
                message="'name' must be a non-empty string.",
            )
        )

    if not spec.intent.summary.strip():
        issues.append(
            Issue(
                severity="error",
                component="intent",
                message="'intent.summary' must be a non-empty string.",
            )
        )

    if len(spec.acceptance_criteria) == 0:
        issues.append(
            Issue(
                severity="error",
                component="acceptance_criteria",
                message=(
                    "'acceptance_criteria' must contain at least one criterion. "
                    "A spec with no acceptance criteria cannot be verified."
                ),
            )
        )

    for ac in spec.acceptance_criteria:
        if ac.input_pattern is None:
            issues.append(
                Issue(
                    severity="warning",
                    component=f"acceptance_criteria[{ac.id}]",
                    message=(
                        f"Acceptance criterion '{ac.id}' has no input_pattern. "
                        "It will be emitted as a skipped test stub."
                    ),
                )
            )

    if len(spec.constraints) == 0:
        issues.append(
            Issue(
                severity="warning",
                component="constraints",
                message="'constraints' is empty. Consider documenting at least one constraint.",
            )
        )

    if len(spec.non_goals) == 0:
        issues.append(
            Issue(
                severity="warning",
                component="non_goals",
                message="'non_goals' is empty. Consider documenting explicit non-goals.",
            )
        )

    if len(spec.dependencies) == 0:
        issues.append(
            Issue(
                severity="info",
                component="dependencies",
                message="'dependencies' is empty.",
            )
        )

    is_operational = all(issue.severity != "error" for issue in issues)
    return ValidationReport(is_operational=is_operational, issues=issues)
