# skill_self_verification.md

## Skill: Run Spec-Derived Tests

**When to apply.** After Generate Under Constraints produces a diff, before the diff is surfaced.

**Inputs.**

- The diff from Generate Under Constraints.
- The parsed unit section from Ingest Spec.
- The test framework is available in the codebase.

**Outputs.** A structured verification report with tests run, tests passed, tests failed, and each failure categorized. If verification halts on an unresolvable failure, a structured flag is set.

**Process.**

- Identify the tests to run. Derive tests in each category:
  - Property-based tests from invariants.
  - Contract tests from contracts.
  - Generative tests from acceptance criteria.
  - Example-based tests from specific scenarios and edge cases.
- If tests in any category cannot be derived because the spec content is missing, surface the gap as a blocker.
- Apply the tests to the diff. Apply the diff to a working copy. Run the tests. Collect the full set of results.
- Categorize each result:
  - Pass: the code honors the spec content from which the test was derived.
  - Failure: a disagreement that requires analysis (see categorization below).
  - Skip: the test could not be run.
  - Error: the test itself raised an unhandled exception.
- Produce the verification report. Include the spec content each test was derived from and the diff content each test exercised. Structure so the human reviewer can locate each result against the spec and code.
- If failures cannot be resolved by code regeneration, produce a structured flag and halt.

## Skill: Self-Critique

**When to apply.** After running Spec-Derived Tests, it produces a verification report with passes or resolved failures before the diff is surfaced.

**Inputs.**

- The diff from Generate Under Constraints.
- The verification report.
- The parsed unit section from Ingest Spec.

**Outputs.** A self-critique report that confirms the diff is ready for review or identifies gaps the tests did not catch.

**Process.**

- Re-read the parsed unit section. Read constraints, invariants, contracts, acceptance criteria, non-goals, and dependencies once more, after code generation.
- Examine the diff against each declarative item. For each item, identify the part of the diff responsible for honoring it. If no part of the diff honors a given item, flag the gap. The gap is either a test gap (item satisfied by code, no test exercises) or a code gap (item not satisfied by the code).
- Examine the diff against the non-goals. If the diff touches code outside the unit's scope, flag the violation.
- Examine the diff for unused dependencies. For each declared dependency, verify that the diff uses it or declares the condition for use. Flag unused dependencies.
- Examine the diff for novel decisions. Identify any choice made during generation that was not explicitly specified and could have gone another way. Record each novel decision with a rationale.
- Produce the self-critique report. Append to the verification report.

## Decision Rules

- When a spec-derived test fails, do not silently modify the test until it passes. If the test is wrong, the spec is wrong; route through the human reviewer.
- When code passes all tests but self-critique identifies a gap, do not declare completion. Surface the gap.
- When the diff contains code not exercised by any test, flag the code as unverified.
- When the same test passes against the code but was generated alongside it, treat it with suspicion. Run an independently-generated test.
- When two acceptance criteria contradict each other, halt and surface as a spec problem.

## Analyzing Test Failures

A failed test is not always a failure of the code. Categorize:

**Code failure.** Test correctly exercises the spec content; code does not honor it.

- Remedy: Regenerate the code with the failure as feedback. Attempt once. If regeneration also fails, surface as a code gap.

**Spec failure.** Test correctly exercises the spec content; code correctly implements something coherent; spec content itself is wrong or contradictory.

- Remedy: Surface the spec problem with the proposed revision. Halt until the reviewer approves.

**Test failure.** Test does not correctly exercise the spec content (test was generated incorrectly, contains a bug, or makes assumptions the spec does not require).

- Remedy: Regenerate the test from the spec content. If regeneration also fails, reclassify as code or spec failure.

Distinguishing the three is the analytic work of self-verification. Read the failed test output, read the spec content, read the code, and identify which artifact is responsible. Record the classification in the verification report.
