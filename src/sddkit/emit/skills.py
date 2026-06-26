"""SKILL.md emitters.

emit_skill_file() renders one of the three Jinja2 skill templates from
sddkit/emit/templates/, loaded via importlib.resources.
"""
from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING, Literal

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from sddkit.models.spec import Spec

_SKILL_TEMPLATES: dict[str, str] = {
    "spec_ingestion": "skill_spec_ingestion.md.j2",
    "constrained_execution": "skill_constrained_execution.md.j2",
    "self_verification": "skill_self_verification.md.j2",
}

# Top-level ## headings required by each appendix (used by tests and validation).
SKILL_HEADINGS: dict[str, list[str]] = {
    "spec_ingestion": [
        "## Skill: Ingest Spec",
        "## Skill: Decompose Unit",
        "## Decision Rules",
    ],
    "constrained_execution": [
        "## Skill: Plan Execution",
        "## Skill: Generate Under Constraints",
        "## Decision Rules",
        "## Meta-Skill: Detect Spec-Internal Conflicts",
    ],
    "self_verification": [
        "## Skill: Run Spec-Derived Tests",
        "## Skill: Self-Critique",
        "## Decision Rules",
        "## Analyzing Test Failures",
    ],
}


def emit_skill_file(
    spec: "Spec",
    skill_type: Literal["spec_ingestion", "constrained_execution", "self_verification"],
) -> str:
    template_dir = str(files("sddkit.emit").joinpath("templates"))
    env = Environment(
        loader=FileSystemLoader(template_dir),
        keep_trailing_newline=True,
        autoescape=False,
    )
    template = env.get_template(_SKILL_TEMPLATES[skill_type])
    return template.render(spec_name=spec.name)
