---
name: "pdf-digitizer-phase3-case-draft"
description: "Use when implementing or debugging Phase 3 in the `pdf_digitizer` repo, especially case draft seed selection, OCR-to-edit flow, patient reuse flow, value editor behavior, and JSON/PDF output consistency."
---

# PDF Digitizer Phase 3 Case Draft

Use this skill for Phase 3 case-draft seeding and reuse behavior in `pdf_digitizer`.

## Decision flow
1. Treat `case_draft` as the runtime source of truth. OCR JSON is only a seed artifact.
2. Resolve the initial editor state in this order:
   - explicit `case_id`
   - latest case for the same project and input PDF
   - latest case for the same project
   - `result.json` values
   - empty template
3. Skip automatic latest-case loading when starting reuse mode with an explicit patient ID; the operator is about to search and copy.
4. If no case exists yet but project context, OCR result data, or `ignore_result` is present, create a new case draft immediately so edits persist from the first save.
5. When copying for reuse, create a new case with `source_case_id`, mark copied fields as copied, and keep the original case immutable.
6. Record OCR result output only when a result JSON actually seeded the case. `ignore_result` should not leave stale OCR provenance behind.
7. Ensure every field definition exists in editor state even when its value is blank.

## File anchors
- `workflow/case_draft_repository.py`
- `generator/phase3_pipeline.py`
- `editor/value_editor.py`
- `editor/templates/value_editor.html`
- `dashboard/app.py`

## Guardrails
- Never treat OCR output as the long-term source of truth.
- Do not merge template definitions and patient data into one schema.
- Reuse flow must create a new case; it must not overwrite the old case in place.
