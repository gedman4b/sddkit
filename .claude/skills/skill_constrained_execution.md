# skill_constrained_execution.md

## Skill: Plan Execution

**When to apply.** After the Ingest Spec and Decompose Unit produce a parsed unit ready for execution, before code generation.

**Inputs.** The parsed unit section, including all declarative items.

**Outputs.** A plan that maps each declarative item to the code structure that will honor it, the order in which code will be produced, and any flagged potential conflicts.

**Process.**

- List the declarative items. Enumerate every constraint, invariant, contract, and non-goal. Each is a property the code must honor.
- Map each item to a code structure:
  - A constraint that the function must not exceed 100ms: the timeout mechanism.
  - An invariant that counter modification is atomic: the Redis operation choice.
  - A contract that errors return Permitted: the exception handling.
- Record the mapping. Verify each mapping is concrete.
- Identify cross-cutting concerns. Some items apply to all code in the unit rather than to a specific structure:
  - Observability constraints that every code path emits a metric.
  - Data-residency constraints that every storage or logging call must respect.
- Record these as global properties to maintain throughout.
- Sequence the code. Code that other code depends on is produced first. Independent code can be in any order; choose to minimize the working context held at each step.
- Identify potential conflicts. Examine the plan for places where two items might require contradictory code. If a conflict is identified, surface it before generation begins. Do not assume conflicts resolve during generation.
- Produce the plan as output for the next skill.

## Skill: Generate Under Constraints

**When to apply.** After the plan execution produces a plan, during code generation. Apply continuously, not as a single pass.

**Inputs.**

- The plan from Plan Execution.
- The current state of the code being generated.

**Outputs.** A diff against the existing code, expressed in a form a human can review line by line. If any constraint cannot be satisfied, a structured flag is set to identify the unsatisfied item, and execution is halted.

**Process.**

- Generate the next piece of code per the plan's sequence. A piece is a function, method, configuration block, or similar unit.
- Evaluate the piece against the declarative items mapped to it. If the code does not honor a mapped item, regenerate the piece. Do not proceed past a piece that fails to map its items.
- Evaluate the piece against the cross-cutting concerns. Verify the piece does not violate any global property. The metric-emission constraint, the data residency constraint, the logging convention, and similar concerns must be honored by every piece.
- Evaluate the piece against the non-goals. If the piece touches code from a different unit or implements excluded behavior, regenerate to remove the violation.
- Record the piece as part of the diff. Produce the change as a diff against the existing code. Do not produce wholesale file replacements except when files are created or deleted entirely.
- Repeat for the next piece. Track which declarative items have been honored across pieces. An item that no piece has honored is a gap; surface it.
- Produce the output. When all pieces are generated and all items honored, produce the full diff. If any item cannot be honored, produce the structured flag and halt.

## Decision Rules

- When a declarative item appears to require code that violates another item, halt and flag the violation. Do not resolve by choosing.
- When the spec implies a behavior that the declarative layer would forbid, do not generate code for that behavior. Surface as a gap.
- When code that honors the spec would violate a codebase convention, prefer the spec. The spec is authoritative.
- When local code satisfies its piece but would violate a global invariant when composed, regenerate the piece.
- When existing code at the insertion location disagrees with the spec, treat it as potential drift. Surface and resolve before proceeding.

## Meta-Skill: Detect Spec-Internal Conflicts

The spec itself can contain conflicts. Surface them rather than silently resolving.

Spec-internal conflict shapes:

- A constraint and an invariant are jointly unsatisfiable (latency budget vs. verification requirement).
- A contract and an acceptance criterion disagree (returns permitted on error vs. never permits requests that exceed the limit).
- A non-goal and a constraint conflict (do not modify middleware vs. check must run before credential verification).
- A constraint and a dependency conflict (latency budget vs. dependency's response time).

In each case: halt, surface the conflict, do not produce code that approximately satisfies both. Wait for the human reviewer's spec revision.
