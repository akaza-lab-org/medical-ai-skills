# Comparison Checklist

Use this checklist when reviewing preprocessing changes.

## Before Running

- Pick the same source PDF fixtures for before and after runs.
- Confirm settings match across runs.
- Confirm the same redaction rules and manual OCR corrections are applied when relevant.

## Compare First

- `cleaned.txt`
- `ready_for_gemini.txt` or equivalent
- `warnings.json`
- `review.md`
- preview images

## Questions

- Did any clinically meaningful lines disappear?
- Did page furniture return?
- Did record grouping improve or get worse?
- Did OCR suggestions become more plausible?
- Did warning counts change sharply?
- Are changes localized to the intended logic area?

## Escalate

If the artifact change is large and not obviously intentional, inspect `blocks.tsv`, OCR candidate files, and crop previews before merging or shipping the change.
