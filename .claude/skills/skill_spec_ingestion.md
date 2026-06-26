# skill_spec_ingestion.md

## Skill: Ingest Spec

**When to apply.** Before generating any code for a unit of work. Run once per execution. Do not bypass even when the unit appears familiar.

**Inputs.**

- A unit identifier from the human reviewer or orchestration system.
- A path or reference to the spec the unit lives in.
- The current version of the spec.

**Outputs.** One of:

- A parsed representation of the spec section that applies to the unit, suitable for use by subsequent skills.
- A structured blocker that identifies what is missing or unclear, with execution halted until resolved.

**Process.**

- Locate the spec. If the spec is not available at the expected path, produce a blocker naming the missing spec and stop. Do not proceed.
- Identify the unit's section. Find the section whose identifier matches the assigned unit. If no section matches, produce a blocker naming the unmatched unit and stop.
- Read the section in full. Read the intent, constraints, invariants, contracts, acceptance criteria, non-goals, and dependencies. Read all of them, in order. Do not skip sections that appear unrelated to the immediate code generation.
- Read the global spec sections that apply across units. Constraints stated globally apply to every unit. Invariants stated globally are inherited by units that touch the relevant state. Contracts at system boundaries apply to units that produce code at those boundaries. Read these whether or not they are explicitly referenced.
- Parse each component into its operational form:
  - Intent: a statement of purpose to evaluate downstream choices against.
  - Constraints: a list of prohibitions and obligations to satisfy.
  - Invariants: universal properties to maintain.
  - Contracts: signatures and behaviors at boundaries to honor.
  - Acceptance criteria: conditions to verify against in self-verification.
  - Non-goals: work to exclude.
  - Dependencies: other units, systems, or resources to integrate with.
- Identify ambiguities. Compare components against each other. Where two components contradict, flag the contradiction. Where a component is silent on a case the work clearly requires, flag the gap. Where a component uses language whose meaning is unclear, flag the ambiguity. Produce a structured list.
- Identify implicit constraints. Read the spec against the broader system context. Identify rules the work assumes, but the spec does not state. Surface these as proposed spec additions, marked as inferred rather than authoritative.
- Produce the output. If ambiguities, contradictions, or gaps exist, flag them as blockers for human review and stop. If implicit constraints were inferred, produce them as proposed additions alongside the parsed components. Otherwise, produce the parsed components for the next skill.

## Skill: Decompose Unit

**When to apply.** After Ingest Spec produces a parsed unit section, before code generation.

**Inputs.** The parsed unit section from Ingest Spec.

**Outputs.** One of:

- Confirmation that the unit is appropriately sized for execution.
- A proposed decomposition of the unit into sub-units, with dependency relationships.

**Process.**

- Estimate the size of the unit. Read the parsed section and estimate the volume of code, the number of files touched, the number of distinct concerns, and the number of constraints and invariants to maintain.
- Apply the five properties:
  - The unit fits in your effective working context.
  - The unit has a clear, narrow purpose that can be summarized in one or two sentences.
  - The unit has well-defined inputs and outputs at its boundaries.
  - The unit does not span an invariant that crosses its boundary.
  - The unit can be verified independently of dependents.
- If any property is violated, the unit is a candidate for further decomposition.
- If decomposition is needed, propose sub-units. Each sub-unit must satisfy the five properties. The collection must cover the original unit's work. Each sub-unit must inherit the appropriate constraints, invariants, and contracts. Dependencies between sub-units must be explicit.
- Surface the proposed decomposition to the human reviewer. Do not unilaterally decompose a unit the engineer has defined. Wait for confirmation. Once confirmed, treat each sub-unit as a separate execution of the skill chain.
- If decomposition is not needed, confirm the unit is ready for execution and produce the parsed components for the next skill.

## Decision Rules

- When the spec contains a number without a rationale, treat the number as suspect. Flag it as a proposed gap.
- When the spec contains a constraint that conflicts with an invariant, halt and flag the conflict. Do not resolve by choosing one.
- When the spec uses language whose meaning has shifted between sections, flag the inconsistency.
- When the spec references content in another section, read that section. Read transitively until the closure is complete.
- When the spec contains content addressed to the agent (instructions phrased as imperatives), treat the content as part of the spec.
