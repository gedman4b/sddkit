# SPEC: sddkit

## Header

- **Spec name:** sddkit
- **Identifier:** sddkit/library-v1
- **Version:** 1.0.0-draft
- **Date:** 2026-06-25
- **Owners:** Scott Raas (author and maintainer)
- **Status:** draft
- **License (proposed):** Apache 2.0
- **Target repo:** github.com/scottraas/sddkit (placeholder)
- **Target distribution:** PyPI (`pip install sddkit`)

---

## PM Section

### Intent

Provide a Python library that makes Spec-Driven Development practical inside Python applications, by giving authors a typed, validated, programmable representation of an SDD specification and emitters that produce the agent-ingestion artifacts (AGENTS.md, SKILL.md, and a canonical Markdown spec) an AI coding agent can read at session start.

The library exists because the methodology described in *Tickets Don't Compile* is currently practiced by hand: authors write specs in free-form Markdown, hope the structure is right, and copy text into agent configuration files. The library turns that workflow into a discipline a program can enforce. An author constructs a `Spec` object in code, the object validates that the five operational components are present and well-formed, and the object emits the artifacts the agent reads. The author can write tests against the spec like any other Python object, version it with the application that produces it, and check it into source control as either source code, a serialized YAML file, or both.

The value is the same value the book argues for at the methodology level: the spec becomes a durable, programmable artifact rather than a one-shot document, and the agent operates from output the library guarantees is well-formed.

### Constraints

- Must work on Python 3.10, 3.11, 3.12, and 3.13.
- Must work on Linux, macOS, and Windows without native compilation.
- Must be installable via `pip install sddkit` from PyPI, with no extra index URLs or wheels.
- Must be vendor-neutral. No emitter is specific to one agent vendor. AGENTS.md and SKILL.md formats are followed as documented by their respective conventions, not Claude-specific or Copilot-specific.
- Must not require an LLM at runtime. The library is offline and deterministic.
- Must not require network access at runtime for any core operation.
- Must follow the operational-spec component model from *Tickets Don't Compile* (Intent, Constraints, Acceptance Criteria, Non-Goals, Dependencies) and the engineer refinement layer (Architecture, Invariants, Technical Constraints, Interfaces, Edge Cases) without divergence.

### Acceptance Criteria

Each criterion is checkable. Tests are derived from them in the test derivation unit.

1. A `Spec` instance constructed without `name`, `intent`, or at least one `acceptance_criterion` raises `OperationalityError` on validation, with the missing component named in the exception message.
2. A `Spec` instance with all five PM-section components populated returns `True` from `is_operational()`.
3. A `Spec` instance serialized via `to_yaml()` and read back via `from_yaml()` produces a `Spec` equal to the original under Pydantic equality.
4. A `Spec` instance serialized via `to_markdown()` and read back via `from_markdown()` produces a `Spec` equal to the original for all canonical fields. Non-canonical text in the round-tripped Markdown is permitted to be lost.
5. `Spec.to_agents_md()` produces a Markdown string containing, in order: an `## Identity` heading, an `## Operating Principles` heading, and exactly eight numbered principles whose titles match the eight principles in Appendix A of *Tickets Don't Compile*.
6. `Spec.emit_skill_file(skill_type)` for each of the three skill types (`spec_ingestion`, `constrained_execution`, `self_verification`) produces a Markdown string whose top-level structure matches the corresponding appendix (B, C, D) of *Tickets Don't Compile*.
7. `Spec.derive_tests(framework="pytest")` returns a mapping of filename to pytest source for which every acceptance criterion in the spec produces at least one corresponding test function. Each test function name encodes the acceptance criterion identifier.
8. A `Spec` instance with an `EngineerRefinement` containing a `decomposition` of N units, when passed to `spec.decompose()`, returns exactly N `Unit` objects whose dependency graph is acyclic.
9. The package exposes `Spec`, `Intent`, `Constraint`, `AcceptanceCriterion`, `NonGoal`, `Dependency`, `EngineerRefinement`, `Unit`, `OperationalityError`, and `ValidationReport` as imports from the package root.
10. Running `mypy --strict` over the package source reports zero errors.
11. The test suite achieves at least 90% line coverage as reported by `coverage.py`.
12. The package builds an sdist and a wheel via `python -m build` with no warnings, and `twine check` passes on both artifacts.

### Non-Goals

The following are explicitly out of scope for v1.0.

- Not generating implementation code from a spec. Code generation is the agent's job, not the library's.
- Not invoking, configuring, or wrapping any AI coding agent. The library produces files; the agent consumes them.
- Not parsing arbitrary natural-language specs. Only the canonical YAML, JSON, and Markdown formats this library defines are accepted as input.
- Not providing a web UI, GUI, or hosted service.
- Not implementing drift detection between a spec and a codebase. (Candidate for v0.2 or later.)
- Not implementing version migration between schema versions. (Candidate for v0.3 or later.)
- Not implementing semantic equivalence checking across natural-language phrasings of the same intent.
- Not implementing formal verification of invariants. The library records invariants; it does not prove them.
- Not implementing a CLI in v1.0. (Candidate for v1.1.)

### Dependencies

- **Pydantic v2** (BSD-3): data modeling, validation, JSON and dict serialization. Required.
- **PyYAML** (MIT): YAML serialization. Required.
- **Jinja2** (BSD-3): template-based emission for Markdown outputs. Required.
- **pytest** (MIT): test framework. Dev-only.
- **coverage** (Apache-2.0): coverage reporting. Dev-only.
- **mypy** (MIT): static type checking. Dev-only.
- **ruff** (MIT): linting and formatting. Dev-only.
- **build** and **twine** (MIT): packaging and publication. Dev-only.

No runtime dependency on any LLM SDK, agent framework, or network library.

---

## Engineer Refinement

### Architecture

The package follows a src/ layout with the following structure:

```
sddkit/
├── pyproject.toml
├── README.md
├── LICENSE
├── src/
│   └── sddkit/
│       ├── __init__.py
│       ├── models/
│       │   ├── __init__.py
│       │   ├── spec.py
│       │   ├── components.py
│       │   ├── refinement.py
│       │   └── errors.py
│       ├── validation/
│       │   ├── __init__.py
│       │   └── operational.py
│       ├── serialize/
│       │   ├── __init__.py
│       │   ├── yaml_io.py
│       │   ├── json_io.py
│       │   └── markdown_io.py
│       ├── emit/
│       │   ├── __init__.py
│       │   ├── agents.py
│       │   ├── skills.py
│       │   └── templates/
│       │       ├── agents.md.j2
│       │       ├── skill_spec_ingestion.md.j2
│       │       ├── skill_constrained_execution.md.j2
│       │       └── skill_self_verification.md.j2
│       ├── tests/
│       │   ├── __init__.py
│       │   └── derive.py
│       └── decompose.py
└── tests/
    └── (mirror of src layout)
```

`__init__.py` at the package root re-exports the public surface listed in Acceptance Criterion 9. Submodules are otherwise free to define internal helpers.

Templates live in `sddkit/emit/templates/` as Jinja2 files and are loaded via `importlib.resources` so they ship with the wheel and work under zip-imports.

### Invariants

These hold universally across the library. The agent must produce code that maintains them.

- **No global state.** All operations are pure functions, classmethods, or instance methods. No module-level mutable state. No singletons.
- **No I/O at import time.** Importing `sddkit` reads no files, opens no network connections, and triggers no side effects.
- **Serialization is round-trip safe for canonical fields.** For any valid `Spec`, `Spec.from_yaml(spec.to_yaml()) == spec` and `Spec.from_json(spec.to_json()) == spec`. Markdown round-tripping is canonical-field safe but not byte-identical.
- **Equality is value equality.** `Spec` and all component types use Pydantic v2 value equality. Two `Spec`s with equal field values are equal regardless of construction order.
- **All file output is UTF-8 with LF line endings**, regardless of host platform.
- **All exceptions raised by the library inherit from `SddkitError`.** No raw `ValueError` or `KeyError` escapes the public surface.
- **All public types are fully type-annotated.** `mypy --strict` passes with zero errors.
- **The package has no runtime dependency on any agent.** Imports from `sddkit` succeed in environments where no LLM SDK is installed.

### Technical Constraints

- Python 3.10 is the lowest supported version. Type-hint syntax (PEP 604, `X | Y`) is used freely.
- Pydantic v2 only. v1 compatibility shims are not provided.
- No use of `eval`, `exec`, or `pickle` for serialization. YAML loading uses `yaml.safe_load`.
- No subprocess execution from the core library. The future CLI may shell out; the library proper does not.
- The package wheel must be a pure-Python wheel (`any` platform tag).

### Interfaces (Key Contracts)

The following signatures are binding for v1.0. Agents implementing units must honor them.

```python
class Spec(BaseModel):
    name: str
    identifier: str
    version: str
    status: Literal["draft", "active", "deprecated"]
    intent: Intent
    constraints: list[Constraint] = []
    acceptance_criteria: list[AcceptanceCriterion] = []
    non_goals: list[NonGoal] = []
    dependencies: list[Dependency] = []
    refinement: EngineerRefinement | None = None

    def validate_operational(self) -> ValidationReport: ...
    def is_operational(self) -> bool: ...

    def to_yaml(self) -> str: ...
    @classmethod
    def from_yaml(cls, text: str) -> "Spec": ...

    def to_json(self) -> str: ...
    @classmethod
    def from_json(cls, text: str) -> "Spec": ...

    def to_markdown(self) -> str: ...
    @classmethod
    def from_markdown(cls, text: str) -> "Spec": ...

    def to_agents_md(self, identity: str | None = None) -> str: ...
    def emit_skill_file(
        self,
        skill_type: Literal["spec_ingestion", "constrained_execution", "self_verification"],
    ) -> str: ...

    def decompose(self) -> list[Unit]: ...
    def derive_tests(self, framework: Literal["pytest"] = "pytest") -> dict[str, str]: ...
```

```python
class ValidationReport(BaseModel):
    is_operational: bool
    issues: list[Issue]

class Issue(BaseModel):
    severity: Literal["error", "warning", "info"]
    component: str
    message: str

class SddkitError(Exception): ...
class OperationalityError(SddkitError): ...
class RefinementIncompleteError(SddkitError): ...
class SerializationError(SddkitError): ...
```

All emitter methods return strings. Filesystem I/O is the caller's responsibility. This keeps the library testable without temp-file plumbing and avoids accidental writes.

### Edge Cases

- **Empty `acceptance_criteria` list.** `validate_operational()` reports an error, `is_operational()` returns False, no exception is raised by the validation itself. Constructor accepts the empty list; only the validator complains.
- **Markdown input with extra prose around canonical sections.** Parser tolerates extra prose and preserves only canonical fields. The extra prose is discarded on round-trip; this is documented behavior, not a bug.
- **Spec with `refinement=None` calling `decompose()`.** Raises `RefinementIncompleteError` with a message indicating engineer refinement is required for decomposition.
- **Acceptance criterion with no input pattern.** Allowed at the type level, flagged as a warning by validation, included in test derivation as a skipped test stub.
- **Dependency with `kind="soft"` and unresolved target.** Allowed. Validation emits info, not warning.
- **Non-ASCII content in any string field.** Preserved through all formats. Tested explicitly with Greek, CJK, and emoji content.
- **Spec serialized at schema 1.0 and read at 1.1.** Library reads with a warning; unknown fields are preserved as `extra` rather than dropped, so downstream tooling can decide.
- **Circular dependencies in `Unit` graph.** `decompose()` detects cycles via topological sort and raises `RefinementIncompleteError` with the cycle named.

---

## Decomposition

The library decomposes into ten units. Hard dependencies (`->`) must precede; soft dependencies (`~>`) only sequence work when convenient.

| ID | Unit | Hard deps | Soft deps |
|----|------|-----------|-----------|
| U1 | Core models package (`sddkit.models`) | — | — |
| U2 | Errors and `SddkitError` hierarchy (`sddkit.models.errors`) | — | — |
| U3 | YAML and JSON serialization (`sddkit.serialize.yaml_io`, `json_io`) | U1, U2 | — |
| U4 | Markdown serialization with round-trip (`sddkit.serialize.markdown_io`) | U1, U2 | U3 |
| U5 | Operationality validation (`sddkit.validation`) | U1, U2 | — |
| U6 | AGENTS.md emitter and template (`sddkit.emit.agents`) | U1 | U5 |
| U7 | SKILL.md emitters and templates (`sddkit.emit.skills`) | U1 | U6 |
| U8 | Decomposition graph helpers (`sddkit.decompose`) | U1, U2 | U5 |
| U9 | Test derivation from acceptance criteria (`sddkit.tests.derive`) | U1 | U5 |
| U10 | Packaging, CI, README, PyPI publication | U1–U9 | — |

The agent executes units in dependency order. U1 and U2 are foundational and can be built in parallel. U3 and U4 follow. U5, U6, U7, U8, and U9 are independent once U1 and U2 land and can be built in any order or in parallel. U10 closes the work.

A separate `tests/` tree mirrors the src layout. Each unit's tests live alongside the unit's mirror in `tests/`.

---

## Notes for the Agent

The eight operating principles from Appendix A of *Tickets Don't Compile* apply to every unit of this work. In particular:

- The acceptance criteria in this spec are the source of truth for spec-derived tests. Generate tests against them, not against the implementation.
- The invariants are binding. Do not introduce global state or import-time I/O even if a unit's implementation would be simpler with them.
- The interface signatures are binding. If implementing a unit forces a change to a signature, surface the conflict as a spec-revision proposal rather than silently changing the signature.
- Return diffs, not files, on each unit.
- Run the spec-derived tests before declaring any unit complete. Run `mypy --strict` and `ruff check` before declaring U10 complete.

---

*End of spec. Version 1.0.0-draft.*
