# sddkit

A Python library that makes Spec-Driven Development practical inside Python applications.

`sddkit` gives authors a typed, validated, programmable representation of an SDD specification and emitters that produce the agent-ingestion artifacts (AGENTS.md, SKILL.md, and a canonical Markdown spec) an AI coding agent can read at session start.

## Installation

```bash
pip install sddkit
```

Requires Python 3.10 or later.

## Quick Start

```python
from sddkit import (
    Spec, Intent, Constraint, AcceptanceCriterion, NonGoal, Dependency,
    EngineerRefinement, Unit,
)

spec = Spec(
    name="my-service",
    identifier="my-service/v1",
    version="1.0.0",
    status="draft",
    intent=Intent(
        summary="Provide a reliable widget API.",
        details="Serves widget data to downstream consumers with sub-100ms p99 latency.",
    ),
    constraints=[
        Constraint(id="C1", text="Must not depend on any proprietary SDK.", kind="must-not"),
    ],
    acceptance_criteria=[
        AcceptanceCriterion(
            id="AC1",
            text="GET /widgets returns 200 with a JSON array.",
            input_pattern="GET /widgets with valid auth",
        ),
    ],
    non_goals=[NonGoal(id="NG1", text="Not a write API in v1.")],
    dependencies=[Dependency(name="pydantic", kind="hard")],
)

# Validate operationality (five PM-section components populated)
report = spec.validate_operational()
print(report.is_operational)   # True
print(report.issues)           # warnings for any missing optional components

# Serialise and round-trip
yaml_text = spec.to_yaml()
spec2 = Spec.from_yaml(yaml_text)
assert spec2 == spec

# Emit agent-ingestion artifacts
agents_md = spec.to_agents_md()          # AGENTS.md content
skill_md  = spec.emit_skill_file("spec_ingestion")  # Appendix B skill file

# Derive pytest stubs from acceptance criteria
test_files = spec.derive_tests(framework="pytest")
for filename, source in test_files.items():
    print(f"--- {filename} ---")
    print(source)
```

## Core Concepts

`sddkit` implements the operational-spec component model from *Tickets Don't Compile*:

| Component | Class | Required for operationality |
|---|---|---|
| Intent | `Intent` | Yes (required field) |
| Constraints | `list[Constraint]` | Warning if empty |
| Acceptance Criteria | `list[AcceptanceCriterion]` | Yes (error if empty) |
| Non-Goals | `list[NonGoal]` | Warning if empty |
| Dependencies | `list[Dependency]` | Info if empty |

## Serialisation

All three formats round-trip for canonical fields:

```python
spec.to_yaml()      # → YAML string; Spec.from_yaml(text) → Spec
spec.to_json()      # → JSON string; Spec.from_json(text) → Spec
spec.to_markdown()  # → Markdown with YAML front matter; Spec.from_markdown(text) → Spec
```

## Decomposition

```python
from sddkit import EngineerRefinement, Unit

spec_with_refinement = spec.model_copy(update={
    "refinement": EngineerRefinement(
        decomposition=[
            Unit(id="U1", name="Core models", hard_deps=[]),
            Unit(id="U2", name="Serialization", hard_deps=["U1"]),
        ]
    )
})

ordered_units = spec_with_refinement.decompose()
# Returns units in topological (dependency-first) order.
# Raises RefinementIncompleteError if a cycle is detected.
```

## Public API

```python
from sddkit import (
    Spec,
    Intent,
    Constraint,
    AcceptanceCriterion,
    NonGoal,
    Dependency,
    EngineerRefinement,
    Unit,
    ValidationReport,
    OperationalityError,
    RefinementIncompleteError,
    SerializationError,
    SddkitError,
)
```

All exceptions inherit from `SddkitError`.

## Development

```bash
pip install -e ".[dev]"
pytest           # runs tests with coverage
mypy src/sddkit --strict
ruff check src/sddkit
python -m build
twine check dist/*
```

## License

Apache 2.0. See [LICENSE](LICENSE).
