"""Tests derived from SPEC acceptance criteria for U7: SKILL.md emitters.

AC6: emit_skill_file(skill_type) for each of the three skill types produces
     a Markdown string whose top-level structure matches the corresponding
     appendix (B, C, D) of Tickets Don't Compile.

Top-level structure = the ## headings present and their order.
"""

import re

import pytest

from sddkit.emit.skills import SKILL_HEADINGS, emit_skill_file
from sddkit.models.components import Intent
from sddkit.models.spec import Spec

SKILL_TYPES = ["spec_ingestion", "constrained_execution", "self_verification"]

# Expected ## headings per appendix, in order.
EXPECTED_HEADINGS = {
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


def _spec() -> Spec:
    return Spec(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example intent"),
    )


def _h2_headings(md: str) -> list[str]:
    """Return all ## (but not ###) headings from a Markdown string, in order."""
    return re.findall(r"^## .+", md, re.MULTILINE)


# ---------------------------------------------------------------------------
# AC6: each skill type returns a string
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("skill_type", SKILL_TYPES)
def test_ac6_emit_skill_file_returns_string(skill_type: str) -> None:
    result = _spec().emit_skill_file(skill_type)  # type: ignore[arg-type]
    assert isinstance(result, str)
    assert len(result) > 0


# ---------------------------------------------------------------------------
# AC6: top-level structure matches appendix B / C / D
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("skill_type", SKILL_TYPES)
def test_ac6_required_headings_present(skill_type: str) -> None:
    md = _spec().emit_skill_file(skill_type)  # type: ignore[arg-type]
    for heading in EXPECTED_HEADINGS[skill_type]:
        assert heading in md, f"Missing heading '{heading}' in {skill_type} output"


@pytest.mark.parametrize("skill_type", SKILL_TYPES)
def test_ac6_required_headings_in_order(skill_type: str) -> None:
    md = _spec().emit_skill_file(skill_type)  # type: ignore[arg-type]
    positions = [md.index(h) for h in EXPECTED_HEADINGS[skill_type]]
    assert positions == sorted(positions), (
        f"Headings out of order in {skill_type} output"
    )


def test_ac6_spec_ingestion_structure() -> None:
    md = _spec().emit_skill_file("spec_ingestion")
    headings = _h2_headings(md)
    for expected in EXPECTED_HEADINGS["spec_ingestion"]:
        assert expected in headings


def test_ac6_constrained_execution_structure() -> None:
    md = _spec().emit_skill_file("constrained_execution")
    headings = _h2_headings(md)
    for expected in EXPECTED_HEADINGS["constrained_execution"]:
        assert expected in headings


def test_ac6_self_verification_structure() -> None:
    md = _spec().emit_skill_file("self_verification")
    headings = _h2_headings(md)
    for expected in EXPECTED_HEADINGS["self_verification"]:
        assert expected in headings


# ---------------------------------------------------------------------------
# AC6: spec name injected into output
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("skill_type", SKILL_TYPES)
def test_ac6_spec_name_appears_in_output(skill_type: str) -> None:
    md = _spec().emit_skill_file(skill_type)  # type: ignore[arg-type]
    assert "example" in md


# ---------------------------------------------------------------------------
# AC6: via Spec.emit_skill_file method
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("skill_type", SKILL_TYPES)
def test_ac6_via_spec_method(skill_type: str) -> None:
    result = _spec().emit_skill_file(skill_type)  # type: ignore[arg-type]
    direct = emit_skill_file(_spec(), skill_type)  # type: ignore[arg-type]
    # Both paths produce the same output for the same spec.
    assert result == direct


# ---------------------------------------------------------------------------
# SKILL_HEADINGS constant matches expectations
# ---------------------------------------------------------------------------


def test_skill_headings_constant_covers_all_types() -> None:
    assert set(SKILL_HEADINGS.keys()) == set(SKILL_TYPES)


@pytest.mark.parametrize("skill_type", SKILL_TYPES)
def test_skill_headings_constant_matches_expected(skill_type: str) -> None:
    assert SKILL_HEADINGS[skill_type] == EXPECTED_HEADINGS[skill_type]
