from __future__ import annotations


class SddkitError(Exception):
    """Base class for all exceptions raised by sddkit."""


class OperationalityError(SddkitError):
    """Raised when a Spec fails operationality validation."""


class RefinementIncompleteError(SddkitError):
    """Raised when engineer refinement is required but absent or invalid."""


class SerializationError(SddkitError):
    """Raised when serialization or deserialization fails."""
