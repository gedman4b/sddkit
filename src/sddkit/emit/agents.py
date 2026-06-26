"""AGENTS.md emitter.

emit_agents_md() renders the Jinja2 template from sddkit/emit/templates/agents.md.j2
using importlib.resources so the template ships with the wheel and works under
zip-imports.
"""
from __future__ import annotations

from importlib.resources import files
from typing import TYPE_CHECKING

from jinja2 import Environment, FileSystemLoader

if TYPE_CHECKING:
    from sddkit.models.spec import Spec

_DEFAULT_IDENTITY = (
    "You are a spec-driven coding agent. You operate under Spec-Driven Development, "
    "where the specification is the source of truth and the code is the output. "
    "You are the third actor in the workflow, alongside the product manager who writes "
    "intent and the engineer who refines it. Your role is to read the spec, produce code "
    "that honors it, verify the code against the spec's claims, and surface your work to "
    "a human reviewer in a form the reviewer can act on."
)

_PRINCIPLE_TITLES = [
    "Read the spec before generating code.",
    "Surface ambiguity rather than resolve it silently.",
    "Honor the declarative layer.",
    "Stay within scope.",
    "Verify against the spec.",
    "Return diffs, not files.",
    "Refuse rather than guess.",
    "Treat the spec as revisable.",
]


def emit_agents_md(spec: "Spec", identity: str | None = None) -> str:  # noqa: ARG001
    template_dir = str(files("sddkit.emit").joinpath("templates"))
    env = Environment(
        loader=FileSystemLoader(template_dir),
        keep_trailing_newline=True,
        autoescape=False,
    )
    template = env.get_template("agents.md.j2")
    return template.render(identity=identity or _DEFAULT_IDENTITY)


PRINCIPLE_TITLES: list[str] = _PRINCIPLE_TITLES
