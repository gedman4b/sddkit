# reference_patterns.md

## Spec Component Templates

**Intent template:**

```
The {system_component} must {achieve_outcome}, while {preserve_property}, in service of {business_goal_or_user_value}.
```

NOT: "Improve the login experience."

YES: "The login endpoint must prevent credential stuffing attacks from succeeding at scale, while preserving the login experience for legitimate users who occasionally mistype their passwords or use password managers that retry automatically, in service of the security team's goal of reducing account takeovers without increasing support burden."

**Constraint template:**

```
The {system_component} must {not} {action}, per {source_of_rule}.
```

NOT: "Should be fast."

YES: "The rate limit check must not add more than 50ms of p99 latency, derived from the existing authentication endpoint's p95 baseline of 45ms plus 5ms of headroom."

**Invariant template:**

```
At all times during {scope_of_operation}, {property_holds} across {entities_or_states}.
```

NOT: "The counter is updated correctly."

YES: "At all times during the operation of the rate limiter, the failed-attempt counter for any given IP address is modified atomically through a single Redis operation, such that no two concurrent calls for the same IP can interleave their reads, decisions, and writes."

**Contract template:**

```
The {function_or_endpoint} accepts {inputs_with_types_and_preconditions} and returns {outputs_with_types_and_timing_bounds}. On {error_conditions}, it {error_behavior}. The function may {permitted_side_effects} and may not {forbidden_side_effects}.
```

NOT: "The function rate-limits requests."

YES: "The function check_rate_limit(request) accepts a Request with a non-null TrustedSourceIP attribute and returns a RateLimitDecision (Permitted, Denied, or Bypassed) within 100ms of being awaited. On any internal error, the function returns Permitted rather than throwing an exception. The function may emit metrics and structured logs and may not modify the Request object."

**Acceptance criterion template:**

```
When {observable_input_pattern}, then {observable_outcome} within {time_or_consistency_bound}.
```

NOT: "Rate limiting should work."

YES: "When five failed login attempts originate from the same source IP address within a sixty-second window, the sixth attempt from that IP address returns HTTP status code 429 with a Retry-After header set to 60, within the latency budget of the function."

**Non-goal template:**

```
This work does not {action_or_scope}, {related_work_pointer_if_any}.
```

NOT: (omitted)

YES: "This work does not modify the signup endpoint, which has its own rate limiting strategy tracked in ticket AUTH-892, and does not implement CAPTCHA, MFA, or any other interactive challenge."

**Dependency template:**

```
Depends on {system_or_team_or_ticket} for {what_is_needed}; coordinate via {coordination_mechanism}.
```

NOT: "Requires Redis."

YES: "Depends on the production Redis cluster (deployed Q1, owned by the platform team) for limit state storage; no new datastore required; coordinate via the standard async Redis client interface; no special configuration needed beyond connection pooling."

## Decomposition Patterns

**Five-property check:**

- The unit fits in your effective working context.
- The unit has a clear, narrow purpose that can be summarized in one or two sentences.
- The unit has well-defined inputs and outputs at its boundaries.
- The unit does not span an invariant.
- The unit can be verified independently.

**Unit identifier:**

```
{parent_feature}/{unit_purpose}
```

Example: rate-limiter/decision-function

**Dependency notation:**

```
Hard dependency: A -> B    (A must be built after B)
Soft dependency: A ~> B    (A is improved if B is built first)
```

**Unit section structure:**

- An identifier and a one-sentence purpose.
- Inherited declarative items.
- Unit-specific declarative items.
- Inputs and outputs at boundaries.
- Acceptance criteria scoped to the unit.
- Dependencies (hard and soft) with rationale.
- Cross-references to related units.

## Test Specification Patterns

**Property-based test from invariant:**

```
Invariant: {universal_property_statement}
Test:
  Generate {N} inputs satisfying {scope_condition}.
  For each input, execute {system_under_test}.
  Assert {property_holds} after each execution.
  Assert {property_holds} across all executions.
```

**Contract test from contract:**

```
Contract: {input_preconditions} -> {output_postconditions}; {error_model}
Test:
  For each {input_class} in the contract:
    Construct an input satisfying the preconditions.
    Execute {function_under_test}.
    Assert the output satisfies the postconditions.
    Assert the timing satisfies the bound.
  For each {error_condition} in the contract:
    Trigger the condition.
    Assert the function exhibits the specified error behavior.
```

**Generative test from acceptance criterion:**

```
Criterion: When {observable_input_pattern}, then {observable_outcome}.
Test:
  Generate {K} instances of the input pattern, varying {parameters_within_pattern}.
  For each instance, execute {system_under_test}.
  Assert the observable outcome holds for each instance.
```

**Example-based test from edge case:**

```
Edge case: {specific_scenario_from_spec}.
Test:
  Construct the specific input.
  Execute {system_under_test}.
  Assert the specific expected outcome.
```

## Refinement Patterns

**PM intends to engineer technical content.** Engineer adds, without overwriting:

- Architecture
- Invariants
- Decomposition
- Technical constraints
- Interfaces
- Edge cases

**PM acceptance criterion to spec-derived tests.** For each criterion, derive at a minimum:

- One generative test exercises many instances.
- One example-based test for any specific cited scenario.
- If the criterion implies a universal property, one property-based test.
- If the criterion crosses a boundary, one contract test.

**Engineer unit to agent execution plan.** For each unit, the plan maps:

- Each inherited constraint is applied to a code structure.
- Each unit-specific invariant is associated with a code structure.
- Each contract includes a function signature, a return type, and an error model.
- Each non-goal is subject to an exclusion check.
- Each dependency is to an integration point.

**Spec gap to spec-revision proposal.** Structured proposal:

- Gap description.
- Proposed text.
- Location.
- Rationale.

Surface to human reviewer. Update only after approval.

## Spec Document Structure

```
1. Header
   - Spec name and identifier
   - Version number and date
   - Owners
   - Status (draft, active, deprecated)
   - Links to system version(s) this spec describes

2. PM Section
   - Intent
   - Constraints (PM-authored)
   - Acceptance criteria
   - Non-goals
   - Dependencies (PM-authored)

3. Engineer Refinement
   - Architecture
   - Invariants
   - Technical constraints
   - Interfaces
   - Edge cases

4. Decomposition
   - Unit list
   - Dependency graph
   - Sequence

5. Unit Sections (one per unit)
   - Identifier
   - Inherited declarative items
   - Unit-specific declarative items
   - Inputs and outputs
   - Acceptance criteria scoped to the unit
   - Dependencies with rationale
   - Cross-references

6. Change Log
   - Entries in reverse chronological order
```

## Versioning Patterns

**Version format:** MAJOR.MINOR.PATCH

- MAJOR: breaking changes to contracts or intent.
- MINOR: additive changes.
- PATCH: clarifications, corrections, formatting.

**Change log entry:**

```
{ISO-8601 date} │ {author} │ {component changed} │ {brief description}
Rationale: {why the change was made}
References: {ticket, PR, or incident identifiers}
```

**Inline annotation:**

```
{spec content}
[Annotation: {date} │ {author}: {note about the content}]
```

**Deprecation:**

```
[DEPRECATED as of {date} │ {author}]
{original content, preserved for reference}
[Replacement: {section_pointer}]
```
