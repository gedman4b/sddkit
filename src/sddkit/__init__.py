"""sddkit — Spec-Driven Development toolkit for Python."""

from sddkit.models.components import (
    AcceptanceCriterion,
    Constraint,
    Dependency,
    Intent,
    NonGoal,
    ValidationReport,
)
from sddkit.models.refinement import EngineerRefinement, Unit
from sddkit.models.spec import Spec

# OperationalityError is defined in U2 (sddkit.models.errors).
# The import below will be populated when U2 lands.
try:
    from sddkit.models.errors import OperationalityError  # type: ignore[attr-defined]
except ImportError:
    pass

__all__ = [
    "AcceptanceCriterion",
    "Constraint",
    "Dependency",
    "EngineerRefinement",
    "Intent",
    "NonGoal",
    "OperationalityError",
    "Spec",
    "Unit",
    "ValidationReport",
]
