"""Markdown serialization for Spec.

Format: YAML front matter (all canonical fields) followed by a
human-readable Markdown body. from_markdown() parses only the front
matter and ignores everything after the closing --- delimiter, so
hand-authored prose around the canonical data is silently discarded
on round-trip (documented behaviour per spec AC4 edge case).
"""
from __future__ import annotations

import re
from typing import TYPE_CHECKING, Any

import yaml
from jinja2 import Environment

from sddkit.models.errors import SerializationError

if TYPE_CHECKING:
    from sddkit.models.spec import Spec

_FRONT_MATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|$)", re.DOTALL)

_ENV = Environment(keep_trailing_newline=True, autoescape=False)

_TEMPLATE = _ENV.from_string(
    """\
---
{{ front_matter }}
---

# {{ name }}

{{ summary }}
"""
)


def spec_to_markdown(spec: "Spec") -> str:
    try:
        data: Any = spec.model_dump(mode="json")
        front_matter = yaml.dump(
            data,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ).rstrip()
        return _TEMPLATE.render(
            front_matter=front_matter,
            name=spec.name,
            summary=spec.intent.summary,
        )
    except Exception as exc:
        raise SerializationError(str(exc)) from exc


def spec_from_markdown(text: str) -> "Spec":
    from sddkit.models.spec import Spec

    match = _FRONT_MATTER_RE.match(text)
    if not match:
        raise SerializationError(
            "No YAML front matter found in Markdown input. "
            "Expected the document to begin with --- ... ---."
        )
    try:
        data = yaml.safe_load(match.group(1))
        if not isinstance(data, dict):
            raise SerializationError("Front matter must be a YAML mapping")
        return Spec.model_validate(data)
    except SerializationError:
        raise
    except Exception as exc:
        raise SerializationError(str(exc)) from exc
