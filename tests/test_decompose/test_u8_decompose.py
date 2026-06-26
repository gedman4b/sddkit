"""Tests derived from SPEC acceptance criteria for U8: decomposition graph helpers.

AC8: A Spec with an EngineerRefinement containing a decomposition of N units,
     when passed to spec.decompose(), returns exactly N Unit objects whose
     dependency graph is acyclic.

Edge cases per spec:
  - refinement=None raises RefinementIncompleteError.
  - Circular dependencies raise RefinementIncompleteError with the cycle named.
"""

import pytest

from sddkit.decompose import decompose_spec
from sddkit.models.components import Intent
from sddkit.models.errors import RefinementIncompleteError, SddkitError
from sddkit.models.refinement import EngineerRefinement, Unit
from sddkit.models.spec import Spec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spec(units: list[Unit] | None = None, refinement: EngineerRefinement | None = ...) -> Spec:  # type: ignore[assignment]
    if refinement is ...:
        refinement = EngineerRefinement(decomposition=units or [])
    return Spec(
        name="example",
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example"),
        refinement=refinement,
    )


def _units(*specs: tuple[str, list[str]]) -> list[Unit]:
    """Quick builder: each tuple is (id, hard_deps)."""
    return [Unit(id=uid, name=uid, hard_deps=deps) for uid, deps in specs]


# ---------------------------------------------------------------------------
# Edge case: refinement=None raises RefinementIncompleteError
# ---------------------------------------------------------------------------


def test_decompose_no_refinement_raises() -> None:
    spec = _spec(refinement=None)
    with pytest.raises(RefinementIncompleteError):
        spec.decompose()


def test_decompose_no_refinement_error_is_sddkit_error() -> None:
    spec = _spec(refinement=None)
    with pytest.raises(SddkitError):
        spec.decompose()


def test_decompose_no_refinement_message_mentions_refinement() -> None:
    spec = _spec(refinement=None)
    with pytest.raises(RefinementIncompleteError, match="refinement"):
        spec.decompose()


# ---------------------------------------------------------------------------
# AC8: returns exactly N Unit objects
# ---------------------------------------------------------------------------


def test_ac8_empty_decomposition_returns_empty_list() -> None:
    assert _spec(units=[]).decompose() == []


def test_ac8_single_unit_returns_one_unit() -> None:
    result = _spec(units=[Unit(id="U1", name="Core")]).decompose()
    assert len(result) == 1
    assert result[0].id == "U1"


def test_ac8_n_units_returns_n_unit_objects() -> None:
    units = _units(("U1", []), ("U2", ["U1"]), ("U3", ["U1"]))
    result = _spec(units=units).decompose()
    assert len(result) == 3


def test_ac8_returned_units_are_unit_instances() -> None:
    units = _units(("U1", []), ("U2", ["U1"]))
    for u in _spec(units=units).decompose():
        assert isinstance(u, Unit)


def test_ac8_all_original_unit_ids_present_in_result() -> None:
    units = _units(("U1", []), ("U2", ["U1"]), ("U3", ["U2"]))
    result_ids = {u.id for u in _spec(units=units).decompose()}
    assert result_ids == {"U1", "U2", "U3"}


# ---------------------------------------------------------------------------
# AC8: dependency graph is acyclic — valid orderings
# ---------------------------------------------------------------------------


def test_ac8_linear_chain_topological_order() -> None:
    # U1 → U2 → U3; expected order: U1, U2, U3
    units = _units(("U1", []), ("U2", ["U1"]), ("U3", ["U2"]))
    result = _spec(units=units).decompose()
    ids = [u.id for u in result]
    assert ids.index("U1") < ids.index("U2")
    assert ids.index("U2") < ids.index("U3")


def test_ac8_diamond_dependency_topological_order() -> None:
    # U1 → U2, U1 → U3, U2 → U4, U3 → U4
    units = _units(("U1", []), ("U2", ["U1"]), ("U3", ["U1"]), ("U4", ["U2", "U3"]))
    result = _spec(units=units).decompose()
    ids = [u.id for u in result]
    assert ids.index("U1") < ids.index("U2")
    assert ids.index("U1") < ids.index("U3")
    assert ids.index("U2") < ids.index("U4")
    assert ids.index("U3") < ids.index("U4")


def test_ac8_no_deps_any_order_all_returned() -> None:
    units = _units(("U1", []), ("U2", []), ("U3", []))
    result = _spec(units=units).decompose()
    assert {u.id for u in result} == {"U1", "U2", "U3"}


def test_ac8_soft_deps_respected_in_ordering() -> None:
    units = [
        Unit(id="U1", name="U1", hard_deps=[], soft_deps=[]),
        Unit(id="U2", name="U2", hard_deps=[], soft_deps=["U1"]),
    ]
    result = _spec(units=units).decompose()
    ids = [u.id for u in result]
    assert ids.index("U1") < ids.index("U2")


# ---------------------------------------------------------------------------
# Edge case: circular dependencies raise RefinementIncompleteError
# ---------------------------------------------------------------------------


def test_ac8_simple_cycle_raises() -> None:
    units = _units(("U1", ["U2"]), ("U2", ["U1"]))
    with pytest.raises(RefinementIncompleteError):
        _spec(units=units).decompose()


def test_ac8_self_loop_raises() -> None:
    units = _units(("U1", ["U1"]),)
    with pytest.raises(RefinementIncompleteError):
        _spec(units=units).decompose()


def test_ac8_three_node_cycle_raises() -> None:
    units = _units(("U1", ["U3"]), ("U2", ["U1"]), ("U3", ["U2"]))
    with pytest.raises(RefinementIncompleteError):
        _spec(units=units).decompose()


def test_ac8_cycle_error_names_cycle_participants() -> None:
    units = _units(("UA", ["UB"]), ("UB", ["UA"]))
    with pytest.raises(RefinementIncompleteError, match="UA|UB"):
        _spec(units=units).decompose()


def test_ac8_cycle_error_is_sddkit_error() -> None:
    units = _units(("U1", ["U2"]), ("U2", ["U1"]))
    with pytest.raises(SddkitError):
        _spec(units=units).decompose()


# ---------------------------------------------------------------------------
# Edge case: unknown dependency reference
# ---------------------------------------------------------------------------


def test_unknown_dep_raises_refinement_incomplete_error() -> None:
    units = [Unit(id="U1", name="U1", hard_deps=["U99"])]
    with pytest.raises(RefinementIncompleteError, match="U99"):
        _spec(units=units).decompose()


def test_unknown_soft_dep_raises_refinement_incomplete_error() -> None:
    units = [Unit(id="U1", name="U1", soft_deps=["UNKNOWN"])]
    with pytest.raises(RefinementIncompleteError, match="UNKNOWN"):
        _spec(units=units).decompose()


# ---------------------------------------------------------------------------
# Via decompose_spec function directly
# ---------------------------------------------------------------------------


def test_decompose_spec_function_matches_method() -> None:
    units = _units(("U1", []), ("U2", ["U1"]))
    spec = _spec(units=units)
    assert decompose_spec(spec) == spec.decompose()
