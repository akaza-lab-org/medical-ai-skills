---
name: regression-checker
description: Check preprocessing or extraction changes for regressions by comparing review artifacts, counts, warnings, and representative output files before and after a code change. Use when modifying PDF crop logic, OCR handling, line cleanup, warning detection, redaction refresh, or any pipeline step that can silently change downstream text quality.
---

# Regression Checker

Treat preprocessing changes as output-quality changes, not just code changes.

Prefer this skill when edits can alter text retention, chronology, OCR dates, masking, warnings, or review artifacts without causing test failures.

## Workflow

1. Choose representative fixtures.
   Use at least one easy PDF and one troublesome PDF.
   Include documents with cropped headers, date OCR candidates, and warning-prone lines when possible.

2. Capture the before state.
   Keep the relevant output bundle from the current implementation.
   Compare artifacts, not only console logs.

3. Run the changed code on the same fixtures.
   Preserve identical settings such as crop thresholds, first-page handling, preview zoom, and redaction rule sets.

4. Compare high-signal artifacts first.
   Review:
   - `cleaned.txt`
   - prompt-ready derivative
   - `warnings.json`
   - `review.md`
   - preview images
   - OCR candidate and correction files when date logic changed

5. Investigate count deltas before reading every line.
   Compare cleaned line count, detected record count, merged date count, warning count, and OCR guess count.
   Large changes are often the fastest path to the regression.

6. Decide whether the delta is an improvement, a tolerated change, or a regression.
   A changed output is not automatically wrong, but it must be explainable.

## What To Check

- Missing clinical lines after crop tuning
- Reintroduced headers, page numbers, or footer noise
- Broken chronology grouping
- Lost or altered date OCR guesses
- Warning floods or warning disappearance
- Prompt-ready output drifting away from cleaned text
- Redaction-derived outputs becoming stale after upstream changes

## What To Read Next

- Read `references/comparison-checklist.md` for a concrete comparison pass.
- Read `references/change-signals.md` for the most meaningful counters and artifacts to inspect.

## Implementation Notes

- Prefer comparing saved files in output directories over eyeballing raw terminal output.
- If automated tests are thin, use artifact diffing as the primary guardrail.
- When possible, keep one known-problem PDF fixture specifically for date OCR and one for header/footer crop tuning.
