from __future__ import annotations

from typing import TYPE_CHECKING, Any

import yaml

from sddkit.models.errors import SerializationError

if TYPE_CHECKING:
    from sddkit.models.spec import Spec


def spec_to_yaml(spec: "Spec") -> str:
    try:
        data: Any = spec.model_dump(mode="json")
        return yaml.dump(data, allow_unicode=True, sort_keys=False, default_flow_style=False)
    except Exception as exc:
        raise SerializationError(str(exc)) from exc


def spec_from_yaml(text: str) -> "Spec":
    from sddkit.models.spec import Spec

    try:
        data = yaml.safe_load(text)
        if not isinstance(data, dict):
            raise SerializationError("Expected a YAML mapping at the top level")
        return Spec.model_validate(data)
    except SerializationError:
        raise
    except Exception as exc:
        raise SerializationError(str(exc)) from exc
