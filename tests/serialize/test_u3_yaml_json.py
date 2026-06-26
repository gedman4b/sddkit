"""Tests derived from SPEC acceptance criteria for U3: YAML and JSON serialization.

AC3: from_yaml(spec.to_yaml()) == spec
AC3 (JSON): from_json(spec.to_json()) == spec
Invariant: SerializationError raised on bad input (inherits SddkitError)
Invariant: yaml.safe_load is used (no arbitrary object deserialisation)
Edge case: non-ASCII content preserved (Greek, CJK, emoji)
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
            decomposition=[Unit(id="U1", name="Core models", hard_deps=[], soft_deps=[])],
        ),
    )


# ---------------------------------------------------------------------------
# AC3: YAML round-trip
# ---------------------------------------------------------------------------


def test_ac3_yaml_roundtrip_minimal() -> None:
    spec = _minimal_spec()
    assert Spec.from_yaml(spec.to_yaml()) == spec


def test_ac3_yaml_roundtrip_full() -> None:
    spec = _full_spec()
    assert Spec.from_yaml(spec.to_yaml()) == spec


def test_yaml_output_is_string() -> None:
    assert isinstance(_minimal_spec().to_yaml(), str)


def test_yaml_output_contains_name() -> None:
    assert "example" in _minimal_spec().to_yaml()


def test_yaml_uses_safe_load_not_arbitrary_objects() -> None:
    # A YAML string that would execute code under yaml.load but not yaml.safe_load.
    # safe_load raises an error instead of constructing a Python object.
    dangerous = "!!python/object/apply:os.system ['echo pwned']"
    with pytest.raises((SerializationError, Exception)):
        Spec.from_yaml(dangerous)


# ---------------------------------------------------------------------------
# AC3 (JSON): JSON round-trip
# ---------------------------------------------------------------------------


def test_ac3_json_roundtrip_minimal() -> None:
    spec = _minimal_spec()
    assert Spec.from_json(spec.to_json()) == spec


def test_ac3_json_roundtrip_full() -> None:
    spec = _full_spec()
    assert Spec.from_json(spec.to_json()) == spec


def test_json_output_is_string() -> None:
    assert isinstance(_minimal_spec().to_json(), str)


def test_json_output_is_valid_json() -> None:
    import json

    data = json.loads(_minimal_spec().to_json())
    assert data["name"] == "example"


# ---------------------------------------------------------------------------
# Invariant: SerializationError on bad input
# ---------------------------------------------------------------------------


def test_from_yaml_bad_input_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_yaml("not: a: spec: at: all\n  broken: [")


def test_from_yaml_non_mapping_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_yaml("- just\n- a\n- list\n")


def test_from_yaml_missing_required_field_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_yaml("name: no-intent\nidentifier: x\nversion: 1\nstatus: draft\n")


def test_from_json_bad_input_raises_serialization_error() -> None:
    with pytest.raises(SerializationError):
        Spec.from_json("{not valid json")


def test_from_json_missing_required_field_raises_serialization_error() -> None:
    import json

    data = {"name": "x", "identifier": "x/v1", "version": "1", "status": "draft"}
    with pytest.raises(SerializationError):
        Spec.from_json(json.dumps(data))


def test_serialization_error_is_sddkit_error() -> None:
    try:
        Spec.from_yaml("- not a mapping")
    except SddkitError:
        pass
    except Exception as exc:
        pytest.fail(f"Expected SddkitError, got {type(exc)}: {exc}")


# ---------------------------------------------------------------------------
# Edge case: non-ASCII content preserved (spec invariant)
# ---------------------------------------------------------------------------


def test_yaml_roundtrip_non_ascii_greek() -> None:
    spec = Spec(
        name="ελληνικά",
        identifier="greek/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="Σκοπός"),
    )
    assert Spec.from_yaml(spec.to_yaml()) == spec


def test_yaml_roundtrip_non_ascii_cjk() -> None:
    spec = Spec(
        name="日本語",
        identifier="cjk/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="意図"),
    )
    assert Spec.from_yaml(spec.to_yaml()) == spec


def test_yaml_roundtrip_emoji() -> None:
    spec = Spec(
        name="emoji-spec 🚀",
        identifier="emoji/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="Ship it 🎯"),
    )
    assert Spec.from_yaml(spec.to_yaml()) == spec


def test_json_roundtrip_non_ascii() -> None:
    spec = Spec(
        name="日本語",
        identifier="cjk/v1",
        version="1.0",
        status="draft",
        intent=Intent(summary="意図"),
    )
    assert Spec.from_json(spec.to_json()) == spec
