---
name: phi-redaction-review
description: Review, define, and apply PHI redaction rules to medical text artifacts while preserving auditability and reviewability. Use when a project needs shared redaction rules, case-specific masking, regenerated redacted outputs, residual identifier review, or a safe workflow that keeps original cleaned text separate from redacted derivatives.
---

# PHI Redaction Review

Treat redaction as a review workflow, not a blind search-and-replace pass.

Prefer this skill when medical text artifacts must be de-identified for LLM use, sharing, annotation, or downstream automation.

## Workflow

1. Identify the source artifacts.
   Find the canonical unredacted text outputs first, typically a cleaned text file and an LLM-ready derivative.
   Do not apply masking directly to the only surviving copy of extracted text.

2. Separate rule scopes.
   Store organization-wide or repeatedly used substitutions as shared rules.
   Store encounter-specific or case-specific substitutions as local rules near the case workspace.
   Combine shared rules first, then local rules, so local exceptions can refine the final result.

3. Regenerate derivatives instead of hand-editing outputs.
   Rebuild redacted text files from the canonical unredacted files whenever rules change.
   Regenerate warning outputs after redaction so residual PHI-like strings remain visible to the reviewer.

4. Keep the masking operation simple and auditable.
   Prefer explicit string replacements when the team needs high traceability.
   Use regex only when the pattern is stable and reviewers can still understand what will be changed.
   Record target and replacement values in machine-readable files.

5. Review residual risk after every rule change.
   Inspect the redacted cleaned text and the redacted LLM-ready derivative.
   Review warning lines again after masking because some identifiers may survive, and some warnings may disappear.

6. Preserve provenance.
   Keep original outputs, redacted derivatives, warning files, and rule files side by side.
   Make it easy to answer which rule set produced a given redacted artifact.

## Rule Design

- Prefer pseudonyms or stable abbreviations when chronology or cross-reference must remain readable.
- Prefer blank replacement only when removing the string does not damage sentence meaning or timeline comprehension.
- Avoid broad replacements that can erase clinical meaning, medication names, or department names accidentally.
- Review short targets carefully because they can overmatch common kana, initials, or abbreviations.
- If a rule is likely to affect multiple unrelated cases, promote it to the shared rule set only after confirming it is not overbroad.

## Safe Review Rules

- Never overwrite the canonical `cleaned.txt` or equivalent source artifact.
- Always regenerate `redacted_cleaned.txt` and the redacted prompt-ready derivative from source files.
- Recompute warning outputs from redacted text, not from stale warnings.
- If OCR corrections or date confirmations exist, preserve them separately; do not fold them into redaction logic.

## What To Read Next

- Read `references/rule-structure.md` when designing shared and local rule files.
- Read `references/review-checklist.md` when validating whether de-identification is sufficient for the intended use.

## Implementation Notes

- Favor file-based JSON rule storage with explicit `target` and `replacement` fields.
- If a dashboard exists, surface shared rules, local rules, redacted artifacts, and residual warnings in one place.
- When adapting to another repository, keep the redaction workflow independent from extraction so either side can evolve safely.
