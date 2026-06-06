---
name: "pdf-digitizer-phase2-tuning"
description: "Use when improving or debugging Phase 2 of the `pdf_digitizer` repo, including field resync from Phase 1, coordinate editor behavior, preview alignment, selection UX, scaling, and `edited_fields.xlsx` handling."
---

# PDF Digitizer Phase 2 Tuning

Use this skill for Phase 2 field-definition refreshes and coordinate-editor tuning in `pdf_digitizer`.

## Decision flow
1. Check whether Phase 2 is stale before editing anything: compare `phase1/initial_fields.json` against `phase2/edited_fields.xlsx`.
2. If Phase 1 changed field structure or coordinate conversion, reinitialize Phase 2 from Phase 1 instead of hand-patching the workbook.
3. Back up an existing `edited_fields.xlsx` before reinitializing. Treat reinit as replace-from-source, not merge.
4. If alignment is still wrong after resync, separate the bug into one of three buckets:
   - Phase 1 output units or origin
   - editor transform or interaction rendering
   - preview or export rendering
5. Verify with both browser behavior and saved workbook output; do not trust raw coordinates alone.
6. Keep field IDs stable across resync when possible because downstream Phase 3 mappings depend on them.
7. Add regression tests for stale detection, reinitialize behavior, or coordinate transforms when changing logic.

## File anchors
- `dashboard/app.py`
- `editor/coord_tool.py`
- `editor/templates/coord_editor.html`
- `projects/<project>/phase1/initial_fields.json`
- `projects/<project>/phase2/edited_fields.xlsx`

## Guardrails
- Do not silently rescale saved coordinates without making the rule visible in the UI.
- Do not merge regenerated Phase 1 fields into Phase 2 heuristically.
- If a user already curated the workbook, preserve a recoverable backup before rewriting it.
