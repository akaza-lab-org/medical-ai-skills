---
name: medical-pdf-preprocess
description: Clean and normalize medical or clinical PDF documents into reviewable text artifacts for downstream LLM extraction, chronology building, or case preparation. Use when working with EMR exports, referral letters, lab reports, progress notes, or scanned clinical PDFs that need header/footer cropping, OCR-assisted date recovery, warning detection, preview images, or human review before structured extraction.
---

# Medical PDF Preprocess

Convert messy clinical PDFs into a small, reviewable output set instead of jumping directly to structured extraction.

Prefer this workflow when dates, headers, repeated page furniture, and PHI-like strings can silently break downstream prompts.

## Workflow

1. Inspect the existing project before inventing a new pipeline.
   Search for scripts, routes, or notebooks that already handle PDF preprocessing, OCR, or review output.
   Prefer extending an existing `preprocess_pdf.py`-style flow instead of creating a second path.

2. Establish the document mix.
   Identify whether the inputs are text PDFs, scanned PDFs, mixed PDFs, or bundles containing non-PDF artifacts.
   Note whether the first page is a cover sheet that should usually be excluded from chronology extraction.

3. Normalize page content before extraction.
   Remove repeated headers and footers by geometric crop, not brittle text replacement.
   Preserve lines that contain clinically meaningful timestamps even when they sit near the cropped region.
   Keep a raw-kept text dump or block-level artifact so review is possible later.

4. Recover chronology anchors.
   Detect date-like anchors from text first.
   If the anchor is partially lost or image-based, generate OCR candidates around the expected date region and store both candidate images and OCR guesses for review.

5. Produce a compact review set.
   Always emit:
   - cleaned text
   - LLM-ready draft text grouped by record date when possible
   - warnings for suspicious lines
   - preview images showing original vs cropped pages
   - a review summary that explains what was kept, dropped, and guessed

6. Keep anonymization review separate from destructive transforms.
   If PHI masking is needed, write redacted derivatives as separate files so the original cleaned output remains inspectable.

7. Validate before handing the text to another model or automation stage.
   Check that chronology count, warning count, and OCR guesses are plausible.
   If no dates are detected, stop and inspect crop settings or OCR candidates before proceeding.

## Decision Rules

- Prefer geometric crop controls such as `header_pt` and `footer_pt` when page furniture is stable across the document.
- Prefer block-level extraction artifacts when tuning crop thresholds or debugging missing lines.
- Prefer merging records by normalized date when multiple chart entries belong to the same day.
- Prefer warning tags over silent heuristics when a line may contain facility names, physician names, referral markers, or other review-worthy content.
- Prefer manual confirmation storage for OCR-corrected dates instead of overwriting guesses without traceability.

## What To Read Next

- Read `references/output-artifacts.md` when you need to interpret or design the output bundle.
- Read `references/tuning-checklist.md` when crop settings, OCR date recovery, or warning behavior need adjustment.

## Implementation Notes

- Keep outputs deterministic and file-based so humans can diff results between runs.
- Store enough intermediate artifacts to debug extraction failures without reopening the whole PDF manually.
- If a dashboard exists, surface preview images, warnings, cleaned text, ready text, and OCR correction inputs in one review screen.
- When adapting this workflow to a new repository, preserve the same artifact contract even if the implementation library changes.
