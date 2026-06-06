---
name: "pdf-digitizer-phase1-tuning"
description: "Use when improving or debugging Phase 1 of the `pdf_digitizer` repo, including PDF analyzer coordinate normalization, page-size conversion, model selection, and `phase1/initial_fields.json` output behavior."
---

# PDF Digitizer Phase 1 Tuning

Use this skill for Phase 1 analyzer output and dashboard launch behavior in `pdf_digitizer`.

## Decision flow
1. Confirm whether the bug is in model detection, coordinate normalization, or dashboard launch wiring before changing anything.
2. Treat raw model output as image-space coordinates. Persist `phase1/initial_fields.json` in PDF points using rendered-page metadata for the same page.
3. For box fields, convert Y with top-plus-height so saved coordinates reference the PDF box origin consistently. Keep point-style mark semantics explicit.
4. If downstream overlays are off, compare `image_width_px` and `image_height_px` against `pdf_width_pt` and `pdf_height_pt` before touching Phase 2 UI code.
5. When Phase 1 runs from the dashboard, verify the selected `model_id` and resolved output path. With a project selected, write to that project's `phase1/initial_fields.json`.
6. Add regression tests for coordinate conversion and any dashboard route that changes model selection or output wiring.

## File anchors
- `analyzer/pdf_analyzer.py`
- `dashboard/app.py`
- `dashboard/templates/dashboard.html`
- `tests/test_pdf_analyzer.py`
- `tests/test_dashboard_app.py`

## Guardrails
- Do not patch Phase 2 rendering to hide a Phase 1 coordinate bug.
- Do not mix image-pixel coordinates and PDF-point coordinates in the same persisted output.
- Keep page-specific dimensions attached to the page that produced the fields.
