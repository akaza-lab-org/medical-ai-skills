---
name: pdf-form-coordinate-tuning
description: Debug and improve coordinate-driven PDF form rendering and export workflows. Use when Codex needs to tune field x/y placement, page assignment, text-box wrapping, font sizing, char spacing, skip rules, or merged coordinate sources such as JSON plus Excel/CSV overrides; also use when browser previews, validation overlays, and generated PDFs disagree.
---

# PDF Form Coordinate Tuning

## Overview

Use this skill to diagnose and tune systems that render application data into fixed PDF form coordinates.

Prefer a narrow, evidence-first workflow: identify which layer is wrong, change one coordinate rule at a time, and verify with actual PDF output instead of trusting raw numbers alone.

## Workflow

1. Classify the failure before editing anything.
   Put the issue in one bucket:
   - source data or field mapping is wrong
   - coordinate source is wrong or stale
   - render math is wrong
   - preview and export use different rules
   - the field should not render at all

2. Trace one broken field end to end.
   Check:
   - field ID used by the app
   - stored value after normalization
   - coordinate record selected for that field
   - whether the renderer's value map actually emits the coordinate file's `data_key`
   - page number
   - x/y origin convention
   - width, height, font, char spacing, and any skip flag

3. Confirm coordinate source precedence.
   If multiple sources exist such as JSON plus Excel or CSV:
   - choose one canonical base
   - merge overrides intentionally and visibly
   - avoid silent replacement that drops properties only present in one source

4. Verify the page and coordinate system.
   Common bugs come from:
   - image-space vs PDF-point coordinates
   - top-left vs bottom-left origin
   - box top vs baseline y semantics
   - fields assigned to the wrong page after schema changes
   - reusing a page's full coordinates when only the header or upper block is actually shared

5. Tune rendering with the smallest possible change.
   Prefer adjusting one of:
   - page
   - x or y
   - box width or height
   - font size
   - line wrapping logic
   - char spacing
   - explicit skip behavior
   Do not rewrite the whole renderer when a single field rule is wrong.

6. Re-verify in all visible outputs.
   Check the browser preview, validation overlay, exported PDF, and any saved workbook or JSON artifact. A fix is not complete until those agree.

## Source Strategy

- Keep field IDs stable across coordinate files, database columns, and UI bindings.
- Prefer a canonical rich format that can hold all render properties. Use secondary files only as operator-editable overrides.
- If an editable workbook lacks properties such as `box_width`, `box_height`, `char_spacing`, `full_width`, or `skip`, merge those from the canonical source instead of losing them.
- Back up hand-edited coordinate files before regeneration or resync.
- Use explicit `coordinate_source` values for reused coordinates. Prefer precise labels such as `page1_same_form`, `page1_shared_header`, or `manually_tuned_from_template_crop`.
- Keep `skip_reason` on intentionally disabled fields until a follow-up issue restores them. Remove it only when the field is wired and visually verified.

## Value Map Wiring Checks

Use this when a PDF renders but sections are blank:

1. List the coordinate keys:

```bash
rg -n '"data_key": "(lung_diagnosis_|colon_history_|colon_test_day)' app/pdf/mappings/*.json
```

2. Search the renderer for matching emitted values:

```bash
rg -n 'lung_diagnosis_|colon_history_|colon_test_day' app/pdf
```

3. Add direct tests against the value map for option groups. Assert the selected option is `True`, neighboring options are `False`, and text fields such as years or dates have the expected value.

4. Generate real PDFs for the option matrix. Use stable names like:
   - `colon_case_01_initial_neg_neg.pdf`
   - `colon_case_02_lastyear_pos_neg.pdf`
   - `lung_case_b_lastyear_with_date.pdf`

If the value map does not emit a key, do not tune coordinates yet. Wire the data first, then render and inspect.

## Text Box Rules

- Distinguish single-line marks, free text, and bounded text boxes. They need different render rules.
- Treat box text as a layout problem, not just an `(x, y)` problem.
- Keep top padding, bottom padding, line leading, wrapping width, and fallback font behavior explicit.
- If auto-fit is used, set a minimum readable font and stop shrinking once readability is at risk.
- If one field repeatedly produces meaningless marks or stray symbols, check whether it should be skipped in PDF output rather than forced through the generic text path.
- For tight single-line fields, `insert_textbox` may silently fail or clip. Consider `insert_text` with a computed baseline and width-based font fitting, then verify visually.

## Validation Pattern

- Use representative real or fixture data, including long text and edge-case fields near page boundaries.
- Compare before and after artifacts, not just code diffs.
- If the app supports layout warnings, run them before generating the final PDF and inspect the flagged fields.
- Add a regression test when changing coordinate transforms, merge precedence, or box wrapping behavior.
- For mark grids, test all values that map to distinct circles, not just the first or default option.

## Printed Ticket Refinement Loop

Use this loop when tuning a compact paper form such as an A5 medical ticket against a scanned original.

1. Lock the paper size and the visual anchors first.
   Decide the immovable blocks before tuning details:
   - QR area
   - header rows
   - signature area
   - specimen-sticker area
   - footer memo box

2. Tune by semantic block, not by individual glyph.
   Move one block at a time:
   - header
   - vitals
   - checklist area
   - footer
   This prevents whack-a-mole coordinate edits.

3. Prefer fewer visual conventions on cramped forms.
   If the original paper uses sparse lines and whitespace, remove unnecessary tables or grids rather than shrinking everything.

4. Use conditional labels instead of symmetric indicators when space is tight.
   Example:
   - show `(無料)` only on free rows
   - omit `有料` markers entirely
   This is often clearer than keeping both paid and free columns.

5. Compare rendered PNGs against the original form after every meaningful change.
   Do not trust coordinate math alone. Render the PDF page and inspect:
   - line collisions
   - cramped rows
   - header breathing room
   - whether labels sit where staff expect to read them

6. Keep preview artifacts with stable names while iterating.
   Use a sequence like:
   - `tmp/<name>_preview_v1.pdf`
   - `tmp/<name>_preview_v2.pdf`
   - matching PNG renders
   This makes regression review fast during live layout tuning.

## Guardrails

- Do not patch preview rendering to hide an export bug.
- Do not silently change coordinate units in persisted files.
- Do not trust spreadsheet edits as complete if another source carries extra render metadata.
- Do not fix a page-mapping bug by moving unrelated fields until the schema-to-page rule is understood.
- Do not auto-correct questionable extracted text unless the product explicitly wants that behavior; often the safer fix is to make review easier.
