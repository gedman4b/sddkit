"""Tests derived from SPEC acceptance criteria for U4: Markdown serialization.

AC4: from_markdown(spec.to_markdown()) == spec for all canonical fields.
     Non-canonical text is permitted to be lost (documented behaviour).
Edge case: extra prose in Markdown input is tolerated and discarded.
Edge case: non-ASCII content preserved.
Invariant: SerializationError (a SddkitError) on bad input.
"""

import pytest

from sddkit.models.components import (
    AcceptanceCriterion,
    Constraint,
    Dependency,
    Intent,
    NonGoal,
)
from sddkit.models.errors import SerializationError, SddkitError
from sddkit.models.refinement import EngineerRefinement, Unit
from sddkit.models.spec import Spec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _minimal_spec() -> Spec:
    return Spec(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example intent", details="Some details"),
    )


def _full_spec() -> Spec:
    return Spec(
        name="full",
        identifier="full/v1",
        version="2.0.0",
        status="active",
        intent=Intent(summary="Full spec", details="All fields populated"),
        constraints=[Constraint(id="C1", text="Must be fast", kind="must")],
        acceptance_criteria=[
            AcceptanceCriterion(id="AC1", text="Does the thing", input_pattern="input")
        ],
        non_goals=[NonGoal(id="NG1", text="Not a web UI")],
        dependencies=[Dependency(name="pydantic", kind="hard", description="Required")],
        refinement=EngineerRefinement(
            architecture="src layout",
            invariants=["No global state"],
            decomposition=[Unit(id="U1", name="Core models")],
        ),
    )


# ---------------------------------------------------------------------------
# AC4: Markdown round-trip for canonical fields
# ---------------------------------------------------------------------------


def test_ac4_markdown_roundtrip_minimal() -> None:
    spec = _minimal_spec()
    assert Spec.from_markdown(spec.to_markdown()) == spec


def test_ac4_markdown_roundtrip_full() -> None:
    spec = _full_spec()
    assert Spec.from_markdown(spec.to_markdown()) == spec


def test_ac4_markdown_roundtrip_all_statuses() -> None:
    for status in ("draft", "active", "deprecated"):
        spec = Spec(
            name="s",
            identifier="s/v1",
            version="1.0",
            status=status,  # type: ignore[arg-type]
            intent=Intent(summary="x"),
        )
        assert Spec.from_markdown(spec.to_markdown()) == spec


def test_to_markdown_returns_string() -> None:
    assert isinstance(_minimal_spec().to_markdown(), str)


def test_to_markdown_contains_name() -> None:
    assert "example" in _minimal_spec().to_markdown()


def test_to_markdown_contains_summary() -> None:
    assert "Example intent" in _minimal_spec().to_markdown()


def test_to_markdown_has_front_matter_delimiters() -> None:
    md = _minimal_spec().to_markdown()
    assert md.startswith("---\n")
    assert "\n---\n" in md


# ---------------------------------------------------------------------------
# Edge case: extra prose around canonical sections is tolerated
# ---------------------------------------------------------------------------


def test_ac4_extra_prose_after_front_matter_is_ignored() -> None:
    spec = _minimal_spec()
    md = spec.to_markdown()
    md_with_extra = md + "\n\n## Extra Section\n\nSome added prose that is not canonical.\n"
    assert Spec.from_markdown(md_with_extra) == spec


def test_ac4_extra_prose_does_not_affect_parsed_fields() -> None:
    spec = _full_spec()
    md = spec.to_markdown() + "\n\n> A blockquote the author added by hand.\n"
    parsed = Spec.from_markdown(md)
    assert parsed.name == spec.name
    assert parsed.constraints == spec.constraints
    assert parsed.acceptance_criteria == spec.acceptance_criteria
    assert parsed.refinement == spec.refinement


# ---------------------------------------------------------------------------
# Edge case: non-ASCII content preserved
# ---------------------------------------------------------------------------


def test_ac4_roundtrip_greek() -> None:
    spec = Spec(
        name="ελληνικά",
        identifier="greek/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="Σκοπός"),
    )
    assert Spec.from_markdown(spec.to_markdown()) == spec


def test_ac4_roundtrip_cjk() -> None:
    spec = Spec(
        name="日本語",
        identifier="cjk/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="意図"),
    )
    assert Spec.from_markdown(spec.to_markdown()) == spec


def test_ac4_roundtrip_emoji() -> None:
    spec = Spec(
        name="emoji 🚀",
        identifier="emoji/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="Ship it 🎯"),
    )
    assert Spec.from_markdown(spec.to_markdown()) == spec


# ---------------------------------------------------------------------------
# Invariant: SerializationError on bad input
# ---------------------------------------------------------------------------


def test_from_markdown_no_front_matter_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_markdown("# Just a heading\n\nNo front matter here.\n")


def test_from_markdown_bad_yaml_in_front_matter_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_markdown("---\n: bad: yaml: [\n---\n")


def test_from_markdown_missing_required_fields_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_markdown("---\nname: no-intent\n---\n")


def test_from_markdown_non_mapping_front_matter_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_markdown("---\n- just\n- a list\n---\n")


def test_serialization_error_is_sddkit_error() -> None:
    try:
        Spec.from_markdown("no front matter")
    except SddkitError:
        pass
    except Exception as exc:
        pytest.fail(f"Expected SddkitError, got {type(exc)}: {exc}")
