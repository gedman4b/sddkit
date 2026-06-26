"""Tests derived from SPEC acceptance criteria for U6: AGENTS.md emitter.

AC5: to_agents_md() produces a Markdown string containing, in order:
     - an ## Identity heading
     - an ## Operating Principles heading
     - exactly eight numbered principles whose titles match the eight
       principles in Appendix A of Tickets Don't Compile.
"""

import re

import pytest

from sddkit.emit.agents import PRINCIPLE_TITLES, emit_agents_md
from sddkit.models.components import Intent
from sddkit.models.spec import Spec

# The eight canonical principle titles from Appendix A (AGENTS.md).
EXPECTED_TITLES = [
    "Read the spec before generating code.",
    "Surface ambiguity rather than resolve it silently.",
    "Honor the declarative layer.",
    "Stay within scope.",
    "Verify against the spec.",
    "Return diffs, not files.",
    "Refuse rather than guess.",
    "Treat the spec as revisable.",
]


def _spec() -> Spec:
    return Spec(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example intent"),
    )


# ---------------------------------------------------------------------------
# AC5: output structure
# ---------------------------------------------------------------------------


def test_ac5_to_agents_md_returns_string() -> None:
    assert isinstance(_spec().to_agents_md(), str)


def test_ac5_contains_identity_heading() -> None:
    md = _spec().to_agents_md()
    assert "## Identity" in md


def test_ac5_contains_operating_principles_heading() -> None:
    md = _spec().to_agents_md()
    assert "## Operating Principles" in md


def test_ac5_identity_heading_precedes_operating_principles() -> None:
    md = _spec().to_agents_md()
    assert md.index("## Identity") < md.index("## Operating Principles")


def test_ac5_exactly_eight_numbered_principles() -> None:
    md = _spec().to_agents_md()
    # Match ### N. Title lines (numbered sub-headings under Operating Principles)
    numbered = re.findall(r"^### \d+\.", md, re.MULTILINE)
    assert len(numbered) == 8


def test_ac5_principle_titles_match_appendix_a_in_order() -> None:
    md = _spec().to_agents_md()
    for i, title in enumerate(EXPECTED_TITLES, start=1):
        pattern = rf"### {i}\. {re.escape(title)}"
        assert re.search(pattern, md), (
            f"Principle {i} not found or title mismatch.\n"
            f"Expected: ### {i}. {title}"
        )


def test_ac5_principle_titles_appear_in_order() -> None:
    md = _spec().to_agents_md()
    positions = []
    for i, title in enumerate(EXPECTED_TITLES, start=1):
        pattern = rf"### {i}\. {re.escape(title)}"
        m = re.search(pattern, md)
        assert m is not None, f"Principle {i} missing"
        positions.append(m.start())
    assert positions == sorted(positions), "Principles are not in order"


# ---------------------------------------------------------------------------
# AC5: identity parameter
# ---------------------------------------------------------------------------


def test_ac5_default_identity_is_non_empty() -> None:
    md = _spec().to_agents_md()
    # Extract text between ## Identity and ## Operating Principles
    match = re.search(r"## Identity\n+(.*?)\n+## Operating Principles", md, re.DOTALL)
    assert match is not None
    assert match.group(1).strip() != ""


def test_ac5_custom_identity_appears_in_output() -> None:
    custom = "You are a custom agent for project X."
    md = _spec().to_agents_md(identity=custom)
    assert custom in md


def test_ac5_custom_identity_appears_in_identity_section() -> None:
    custom = "Custom identity text here."
    md = _spec().to_agents_md(identity=custom)
    identity_section = md[md.index("## Identity"):md.index("## Operating Principles")]
    assert custom in identity_section


def test_ac5_none_identity_uses_default() -> None:
    md_none = _spec().to_agents_md(identity=None)
    md_default = _spec().to_agents_md()
    assert md_none == md_default


# ---------------------------------------------------------------------------
# PRINCIPLE_TITLES constant
# ---------------------------------------------------------------------------


def test_principle_titles_constant_has_eight_entries() -> None:
    assert len(PRINCIPLE_TITLES) == 8


def test_principle_titles_constant_matches_expected() -> None:
    assert PRINCIPLE_TITLES == EXPECTED_TITLES


# ---------------------------------------------------------------------------
# emit_agents_md function directly
# ---------------------------------------------------------------------------


def test_emit_agents_md_called_directly() -> None:
    spec = _spec()
    result = emit_agents_md(spec)
    assert "## Identity" in result
    assert "## Operating Principles" in result


def test_emit_agents_md_custom_identity_directly() -> None:
    spec = _spec()
    result = emit_agents_md(spec, identity="Direct call identity.")
    assert "Direct call identity." in result
