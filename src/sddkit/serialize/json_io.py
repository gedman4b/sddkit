from __future__ import annotations

from typing import TYPE_CHECKING

from sddkit.models.errors import SerializationError

if TYPE_CHECKING:
    from sddkit.models.spec import Spec


def spec_to_json(spec: Spec) -> str:
    try:
        return spec.model_dump_json(indent=2)
    except Exception as exc:
        raise SerializationError(str(exc)) from exc


def spec_from_json(text: str) -> Spec:
    from sddkit.models.spec import Spec

    try:
        return Spec.model_validate_json(text)
    except SerializationError:
        raise
    except Exception as exc:
        raise SerializationError(str(exc)) from exc
