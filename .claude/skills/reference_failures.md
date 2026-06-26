# reference_failures.md

Use this catalog when something has gone wrong. Each entry: symptom, cause, detection, recovery.

## Ingestion Failures

**Missing or Inaccessible Spec.**

- Symptom: Skill chain cannot begin; spec at expected path is missing, empty, or returns permission error.
- Cause: Spec not created, moved, deleted, renamed, or read access not granted.
- Detection: Ingest Spec, Step 1.
- Recovery: Produce a blocker identifying the path and failure mode. Halt. Wait for spec or access.

**Unmatched Unit.**

- Symptom: Spec exists; no section matches the assigned unit identifier.
- Cause: Unit assignment refers to a unit never created, renamed without update, or removed during revision.
- Detection: Ingest Spec, Step 2.
- Recovery: Produce blocker naming the unmatched unit and listing existing units. Halt.

**Genuine Ambiguity.**

- Symptom: Spec content admits multiple defensible interpretations; the alternatives would produce materially different code.
- Cause: The PM or the engineer wrote content that was clear in the author's context but unclear in the current work context.
- Detection: Ingest Spec, Step 6.
- Recovery: Produce a structured flag listing the ambiguous statement, alternative interpretations, and affected sections. Halt.

**Inferred Constraint Conflict.**

- Symptom: Inferred constraint from codebase conventions conflicts with a stated constraint in the spec.
- Cause: Codebase has accumulated conventions that are not reflected in the spec, one of which conflicts with the current spec requirement.
- Detection: Ingest Spec, Step 7.
- Recovery: Surface both constraints with the conflict described. Wait for resolution.

**Decomposition Required But Not Authorized.**

- Symptom: Unit fails the five-property check; further decomposition appears necessary; agent does not have authorization.
- Cause: The engineer's decomposition was too coarse, or the unit acquired complexity not visible at decomposition time.
- Detection: Decompose Unit, Step 2.
- Recovery: Produce proposed decomposition with rationale. Wait for confirmation.

## Execution Failures

**Unsatisfiable Declarative Item.**

- Symptom: During Plan Execution, no code structure can honor a particular constraint, invariant, or contract.
- Cause: Item is impossible to satisfy given existing infrastructure, libraries, or other items in spec.
- Detection: Plan Execution, Step 2 or 5.
- Recovery: Produce a structured flag with unsatisfiable items, analysis, and proposed revisions.

**Spec-Internal Conflict at Generation Time.**

- Symptom: During code generation, a piece is reached where two declarative items demand contradictory code.
- Cause: Spec contains items individually defensible but jointly unsatisfiable.
- Detection: Generate Under Constraints, Step 2.
- Recovery: Halt. Surface conflict per the meta-skill in Constrained Execution.

**Repeated Regeneration Failure.**

- Symptom: A piece fails to honor mapped items. Regeneration produces a piece that also fails.
- Cause: Approach to the piece is structurally wrong; the spec requires something that the agent cannot produce correctly.
- Detection: Generate Under Constraints, Step 2, on second attempt.
- Recovery: Halt. Surface repeated failure with spec content, both attempted pieces, and analysis.

**Non-Goal Violation in Generated Code.**

- Symptom: Generated code touches functionality or files that the non-goals exclude.
- Cause: Piece's mapped responsibility implied a side effect or integration crossing into excluded territory.
- Detection: Generate Under Constraints, Step 4.
- Recovery: Regenerate to remove the violation. If intrinsic to the work, surface as a spec problem.

**Drift Detected at Generation Site.**

- Symptom: Existing code at the insertion location disagrees with the spec.
- Cause: Codebase contains a fix, optimization, or modification applied without a spec update.
- Detection: Generate Under Constraints, Step 5 or Decision Rules.
- Recovery: Halt. Surface drift with spec content and existing code side by side. Wait for reconciliation.

## Verification Failures

**Test Failure: Code Wrong.**

- Symptom: Test fails; test correctly exercises spec content; code does not honor that content.
- Cause: The generation produced code that does not satisfy the spec content.
- Detection: Run Spec-Derived Tests; Analyzing Test Failures.
- Recovery: Regenerate code with failure as feedback. Attempt once. If the regenerated code also fails, reclassify or surface as a code gap.

**Test Failure: Spec Wrong.**

- Symptom: Test fails; test correctly exercises spec content; code correctly implements something coherent; spec content is internally inconsistent or unsatisfiable.
- Cause: Spec contains a constraint, invariant, contract, or criterion that contradicts another item or is impossible.
- Detection: Analyzing Test Failures, after code failure has been ruled out.
- Recovery: Surface spec problem with test, code, and analysis. Halt until the reviewer revises.

**Test Failure: Test Wrong.**

- Symptom: Test fails; test does not correctly exercise the spec content it was derived from.
- Cause: The test was generated incorrectly.
- Detection: Analyzing Test Failures, after code and spec failures have been ruled out.
- Recovery: Regenerate test from spec content. If the regenerated test also fails, reclassify.

**Tests Pass, but Self-Critique Reveals Gap.**

- Symptom: All spec-derived tests pass. Self-critique identifies a declarative item that no test exercises and that no code clearly honors.
- Cause: Test derivation missed an item, code does not honor the item, or both.
- Detection: Self-Critique, Step 2.
- Recovery: Do not declare completion. Surface as a test gap or code gap.

**Same-Source Test Suspicion.**

- Symptom: Test passes against code; test was generated by the same agent invocation that generated the code.
- Cause: Interpretation may have been wrong in the same direction for both artifacts.
- Detection: Decision Rules during Run Spec-Derived Tests.
- Recovery: Run an additional independently-generated test. If it also passes, suspicion resolved; if not, reclassify.

**Acceptance Criteria Contradiction.**

- Symptom: Two acceptance criteria produce contradictory expectations for the same input.
- Cause: Spec contains criteria with overlapping input patterns and disagreeing outcomes.
- Detection: Run Spec-Derived Tests when criteria-derived tests for the same input fail in opposite directions.
- Recovery: Halt. Surface contradiction. Wait for spec revision.

## Cross-Cutting Failures

**Drift Discovered Mid-Execution.**

- Symptom: During any skill, the agent identifies that spec and codebase have diverged.
- Cause: Drift accumulated since last reconciliation.
- Detection: Any phase, when code or behavior contradicts the spec.
- Recovery: Pause current work. Surface drift. Wait for reconciliation. Resume against reconciled spec.
