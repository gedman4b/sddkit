"""Tests derived from SPEC acceptance criteria for U9: test derivation.

AC7: derive_tests(framework="pytest") returns a mapping of filename to pytest
     source for which every acceptance criterion in the spec produces at least
     one corresponding test function. Each test function name encodes the AC id.

Edge case: AC with no input_pattern is included as a skipped test stub.
"""

import re

import pytest

from sddkit.models.components import AcceptanceCriterion, Intent
from sddkit.models.spec import Spec
from sddkit.tests.derive import derive_tests_for_spec


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _spec(*acs: AcceptanceCriterion, name: str = "myspec") -> Spec:
    return Spec(
        name=name,
        identifier="example/v1",
        version="1.0.0",
        status="draft",
        intent=Intent(summary="Example"),
        acceptance_criteria=list(acs),
    )


def _ac(id: str, text: str, pattern: str | None = "input") -> AcceptanceCriterion:
    return AcceptanceCriterion(id=id, text=text, input_pattern=pattern)


def _functions(source: str) -> list[str]:
    """Return all def/async def names from source."""
    return re.findall(r"^def (\w+)", source, re.MULTILINE)


# ---------------------------------------------------------------------------
# AC7: return type is dict[str, str]
# ---------------------------------------------------------------------------


def test_ac7_returns_dict() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    assert isinstance(result, dict)


def test_ac7_values_are_strings() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    for v in result.values():
        assert isinstance(v, str)


def test_ac7_keys_are_strings() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    for k in result.keys():
        assert isinstance(k, str)


def test_ac7_filename_is_py_file() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    assert all(k.endswith(".py") for k in result.keys())


def test_ac7_filename_encodes_spec_name() -> None:
    result = _spec(_ac("AC1", "Does the thing"), name="myproject").derive_tests()
    assert any("myproject" in k for k in result.keys())


# ---------------------------------------------------------------------------
# AC7: every AC produces at least one test function
# ---------------------------------------------------------------------------


def test_ac7_single_ac_produces_at_least_one_test() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    source = next(iter(result.values()))
    assert len(_functions(source)) >= 1


def test_ac7_multiple_acs_each_produce_at_least_one_test() -> None:
    spec = _spec(
        _ac("AC1", "First criterion"),
        _ac("AC2", "Second criterion"),
        _ac("AC3", "Third criterion"),
    )
    result = spec.derive_tests()
    source = next(iter(result.values()))
    fns = _functions(source)
    assert len(fns) >= 3


def test_ac7_test_count_at_least_ac_count() -> None:
    acs = [_ac(f"AC{i}", f"Criterion {i}") for i in range(1, 6)]
    spec = _spec(*acs)
    result = spec.derive_tests()
    source = next(iter(result.values()))
    assert len(_functions(source)) >= 5


# ---------------------------------------------------------------------------
# AC7: test function name encodes the AC identifier
# ---------------------------------------------------------------------------


def test_ac7_function_name_encodes_ac_id() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    source = next(iter(result.values()))
    fns = _functions(source)
    assert any("ac1" in fn.lower() for fn in fns), f"No function encodes AC1 in: {fns}"


def test_ac7_function_names_encode_each_id() -> None:
    spec = _spec(
        _ac("AC1", "First"),
        _ac("AC2", "Second"),
        _ac("AC3", "Third"),
    )
    source = next(iter(spec.derive_tests().values()))
    fns = _functions(source)
    for ac_id in ("ac1", "ac2", "ac3"):
        assert any(ac_id in fn.lower() for fn in fns), f"No function encodes {ac_id}"


def test_ac7_non_standard_id_encoded_in_name() -> None:
    result = _spec(_ac("REQ-42", "Some requirement")).derive_tests()
    source = next(iter(result.values()))
    fns = _functions(source)
    assert any("req" in fn.lower() and "42" in fn for fn in fns)


# ---------------------------------------------------------------------------
# AC7: generated source is valid Python
# ---------------------------------------------------------------------------


def test_ac7_generated_source_compiles() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    for source in result.values():
        compile(source, "<generated>", "exec")  # raises SyntaxError if invalid


def test_ac7_generated_source_imports_pytest() -> None:
    result = _spec(_ac("AC1", "Does the thing")).derive_tests()
    source = next(iter(result.values()))
    assert "import pytest" in source


# ---------------------------------------------------------------------------
# Edge case: AC with no input_pattern → skipped stub
# ---------------------------------------------------------------------------


def test_ac7_no_input_pattern_produces_skipped_stub() -> None:
    result = _spec(_ac("AC1", "No pattern", pattern=None)).derive_tests()
    source = next(iter(result.values()))
    assert "pytest.mark.skip" in source or "pytest.skip" in source


def test_ac7_no_input_pattern_still_produces_a_function() -> None:
    result = _spec(_ac("AC1", "No pattern", pattern=None)).derive_tests()
    source = next(iter(result.values()))
    assert len(_functions(source)) >= 1


def test_ac7_no_input_pattern_function_encodes_ac_id() -> None:
    result = _spec(_ac("AC5", "No pattern ac", pattern=None)).derive_tests()
    source = next(iter(result.values()))
    fns = _functions(source)
    assert any("ac5" in fn.lower() for fn in fns)


def test_ac7_mixed_with_and_without_pattern_all_produce_functions() -> None:
    spec = _spec(
        _ac("AC1", "Has pattern", pattern="x"),
        _ac("AC2", "No pattern", pattern=None),
        _ac("AC3", "Also has pattern", pattern="y"),
    )
    source = next(iter(spec.derive_tests().values()))
    fns = _functions(source)
    assert len(fns) >= 3
    assert "pytest.mark.skip" in source  # AC2 stub is skipped


# ---------------------------------------------------------------------------
# Edge case: empty acceptance_criteria list
# ---------------------------------------------------------------------------


def test_ac7_empty_acs_returns_dict_with_empty_body() -> None:
    spec = _spec()  # no ACs
    result = spec.derive_tests()
    assert isinstance(result, dict)
    source = next(iter(result.values()))
    assert len(_functions(source)) == 0


# ---------------------------------------------------------------------------
# derive_tests_for_spec function directly
# ---------------------------------------------------------------------------


def test_derive_tests_function_matches_method() -> None:
    spec = _spec(_ac("AC1", "Does the thing"))
    assert derive_tests_for_spec(spec) == spec.derive_tests()


def test_derive_tests_framework_pytest_default() -> None:
    spec = _spec(_ac("AC1", "Does the thing"))
    assert spec.derive_tests() == spec.derive_tests(framework="pytest")
