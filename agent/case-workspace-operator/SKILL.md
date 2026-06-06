---
name: case-workspace-operator
description: Organize and operate case-based workspaces for medical PDF preprocessing, review, and follow-up artifacts. Use when a project stores one case per folder with `inputs` and `outputs`, needs stable placement of PDFs/notes/images/labs, writes per-case metadata, or requires a repeatable flow for running preprocessing and reviewing derived artifacts.
---

# Case Workspace Operator

Use a stable per-case folder layout so preprocessing, review, and manual corrections can happen without mixing cases.

Prefer this skill when a repo handles one clinical case, one referral packet, or one review bundle at a time.

## Workflow

1. Create or locate the case root.
   Use one directory per case under a dedicated workspace root such as `case_workspaces/`.
   Prefer stable slugs with timestamp suffixes only when a name collision occurs.

2. Create predictable subfolders.
   Use:
   - `inputs/pdf`
   - `inputs/notes`
   - `inputs/images`
   - `inputs/labs`
   - `outputs/preprocess`

3. Place files by role, not by source.
   Put source PDFs in `inputs/pdf`.
   Put handwritten notes, intake notes, or operator memos in `inputs/notes`.
   Put screenshots or image-only evidence in `inputs/images`.
   Put structured lab files or exports in `inputs/labs`.

4. Keep metadata at case root.
   Write `metadata.json` with case name, source label, creation timestamp, key preprocess settings, and the latest output directory.

5. Process PDFs from the case workspace, not from scattered source paths.
   Copy or upload the source PDFs into the case folder first.
   Run preprocessing against the in-case PDF copies so the case remains reproducible.

6. Keep manual review artifacts inside the case.
   Store redaction rules, OCR corrections, and any follow-up annotations near the case they belong to.

7. Surface the case as one review unit.
   When building a dashboard, show metadata, cleaned text, prompt-ready text, warnings, preview images, OCR candidates, and local/shared masking rules in one case view.

## Operating Rules

- Never mix outputs from multiple patients or encounters in the same case directory.
- Never depend on filenames outside the workspace once the case has been created.
- Prefer copying the source PDF into the case folder over referencing an unstable external path.
- Keep derivative artifacts under `outputs/` so `inputs/` remains source-oriented.
- If multiple PDFs belong to one case, process all files under `inputs/pdf` and record the effective output directory in metadata.

## What To Read Next

- Read `references/layout.md` for the recommended folder contract.
- Read `references/review-flow.md` for the operator checklist from intake through review.

## Implementation Notes

- Keep workspace creation idempotent and explicit.
- Use JSON metadata so dashboards and scripts can read settings consistently.
- When adapting to another project, preserve the case contract even if the UI or preprocessing engine changes.
