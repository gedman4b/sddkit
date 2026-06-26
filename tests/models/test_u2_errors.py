"""Tests derived from SPEC acceptance criteria for U2: error hierarchy.

Invariant: all library exceptions inherit from SddkitError.
AC9: OperationalityError exposed at package root.
"""

import sddkit
from sddkit.models.errors import (
    OperationalityError,
    RefinementIncompleteError,
    SddkitError,
    SerializationError,
)


# ---------------------------------------------------------------------------
# Inheritance invariant
# ---------------------------------------------------------------------------


def test_sddkit_error_is_exception() -> None:
    assert issubclass(SddkitError, Exception)


def test_operationality_error_inherits_sddkit_error() -> None:
    assert issubclass(OperationalityError, SddkitError)


def test_refinement_incomplete_error_inherits_sddkit_error() -> None:
    assert issubclass(RefinementIncompleteError, SddkitError)


def test_serialization_error_inherits_sddkit_error() -> None:
    assert issubclass(SerializationError, SddkitError)


# ---------------------------------------------------------------------------
# Raise and catch
# ---------------------------------------------------------------------------


def test_operationality_error_raises_and_catches_as_sddkit_error() -> None:
    try:
        raise OperationalityError("missing name")
    except SddkitError as exc:
        assert "missing name" in str(exc)


def test_refinement_incomplete_error_raises_and_catches_as_sddkit_error() -> None:
    try:
        raise RefinementIncompleteError("refinement required")
    except SddkitError as exc:
        assert "refinement required" in str(exc)


def test_serialization_error_raises_and_catches_as_sddkit_error() -> None:
    try:
        raise SerializationError("bad yaml")
    except SddkitError as exc:
        assert "bad yaml" in str(exc)


# ---------------------------------------------------------------------------
# AC9: public surface
# ---------------------------------------------------------------------------


def test_ac9_operationality_error_importable_from_package_root() -> None:
    assert hasattr(sddkit, "OperationalityError")
    assert sddkit.OperationalityError is OperationalityError


def test_sddkit_error_importable_from_package_root() -> None:
    assert hasattr(sddkit, "SddkitError")
    assert sddkit.SddkitError is SddkitError
