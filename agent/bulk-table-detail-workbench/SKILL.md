---
name: bulk-table-detail-workbench
description: Design, implement, or refine data-entry screens that combine a fast bulk-edit table with a selected-record detail pane. Use when Codex needs to support rapid row-by-row operational input, inline edits, default values, single-record inspection, bulk save plus per-record save behavior, or smooth navigation from a list into downstream outputs such as PDFs, labels, or patient-specific forms.
---

# Bulk Table Detail Workbench

Use this skill for workflows where users need table-speed entry but still need a focused view for one selected record.

Prefer one coherent workbench over splitting the flow across many disconnected screens unless the detail task is genuinely separate.

## Good Fit

Use this pattern when most of these are true:

- operators work through many records in one sitting
- each row has only a few frequently edited fields
- users sometimes need a closer look at one record
- the row may lead to a downstream action such as PDF output, chart entry, or label printing

If every record needs a long form, use a dedicated record screen instead.

## Core Layout

Use a two-part layout:

- bulk table for rapid scanning and edits
- detail pane for the selected row

Keep the same record visible in both places. The detail pane should reflect the selected row rather than creating a separate temporary record model unless there is a clear reason.

## Workflow

1. Decide the unit of work.
   Define what one row represents:
   - one patient
   - one order
   - one exam
   - one returned document

2. Put only high-frequency fields in the table.
   The table should favor speed:
   - short enums
   - dates
   - yes or no flags
   - compact status labels
   Avoid placing long free text or dense validation messages directly in the grid unless absolutely necessary.

3. Reserve the detail pane for context and safe edits.
   Use it for:
   - selected record summary
   - fields that need better labels or spacing
   - downstream action buttons
   - derived status and warnings

4. Support both bulk save and single-record save.
   Keep the operator fast:
   - save all edited rows together
   - save the selected row immediately when needed
   These paths should converge on the same normalization and persistence logic.

5. Make defaults helpful but reversible.
   Auto-fill obvious defaults, but stop auto-overwriting once the user has made an explicit choice.
   Common pattern:
   - compute a default from existing history or state
   - mark whether the value is still auto-managed
   - disable auto-management after manual toggle or edit

6. Show progress state clearly.
   Give each row a short, stable status such as:
   - pending
   - in progress
   - primary done
   - complete
   The operator should understand what remains without opening each row.

7. Keep downstream actions near the selected row.
   If users often move from data entry into output generation, place those actions in the detail pane for the selected record.

## Data Handling Rules

- Keep one canonical payload shape for save operations.
- Reuse the same normalization for inline edits and detail-pane edits.
- Preserve row identity even if sort or filter order changes.
- Avoid hidden derived-state drift between the table model and detail model.
- If defaults are inferred, store whether the current value is auto-derived or user-set when that distinction affects behavior.

## Interaction Rules

- Highlight the selected row clearly.
- Keep row selection stable after save if the record still exists in the filtered set.
- Do not silently discard unsaved table edits when the selected row changes.
- Prefer compact validation near the edited field and a summary in the detail pane for harder cases.
- If the table includes checkboxes or toggles with inferred defaults, make the auto-vs-manual transition explicit in code even if the UI stays simple.

## API Pattern

Prefer this split:

- list endpoint for the current workset
- bulk update endpoint for many edited rows
- single-record update path that reuses the same backend logic

If downstream documents depend on the same fields, keep the PDF or export layer reading from persisted normalized values rather than transient browser state.

## Validation Checklist

- edit several rows inline, save, and reload
- select one row, edit in detail pane, save, and reload
- confirm defaults apply on first load but stop changing after manual override
- confirm status labels update correctly
- confirm downstream actions use the intended selected record
- test filter or date-range changes without losing the current mental model

## Guardrails

- Do not duplicate business logic separately in table code and detail-pane code.
- Do not let selected-row state drift from the row collection after save.
- Do not auto-reset a user-edited checkbox or enum because source history changed.
- Do not overload the table with low-frequency fields that belong in the detail pane.
- Do not make downstream outputs depend on unsaved client-only edits unless the product explicitly requires that.
