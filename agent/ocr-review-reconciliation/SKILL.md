---
name: ocr-review-reconciliation
description: Design, debug, or refine review workflows where OCR or extraction output seeds a form and humans reconcile it into final saved data. Use when Codex needs to map structured OCR JSON into UI fields, preserve original extraction separately from reviewed values, reload draft OCR state safely, normalize field values before save, or export an auditable correction log.
---

# OCR Review Reconciliation

## Overview

Use this skill when OCR output is useful but not trustworthy enough to become the saved record without human review.

Treat OCR as a seed artifact and the reviewed form submission as the final user-facing truth, while keeping enough provenance to understand what changed and why.

## Workflow

1. Separate the three data layers.
   Keep these distinct:
   - raw OCR or extraction payload
   - normalized values used to prefill the UI
   - final reviewed values saved to the database or output document

2. Normalize before populating the form.
   Convert extraction output into UI-ready values first.
   Typical examples:
   - merge atomic OCR flags into one radio or select value
   - rebuild dates from split era, year, month, and day fields
   - map shorthand booleans or enums into UI labels
   - collapse alternate legacy field names into the current schema

3. Make the review origin visible.
   Highlight OCR-populated fields, keep reload behavior explicit, and let reviewers understand which values came from OCR versus manual input.

4. Preserve the original OCR payload separately.
   Save it as provenance data or sidecar JSON.
   Do not overwrite it with edited values.

5. Save final values through one normalization path.
   The same save path should handle:
   - OCR-seeded edits
   - fully manual edits
   - reload or draft recovery
   Avoid having separate save semantics that drift over time.

6. Record correction diffs intentionally.
   If the product needs auditability, compare original OCR values against the final saved values after normalization and store only meaningful differences.

7. Support safe recovery.
   If browser-local state is used for convenience, treat it as a temporary cache rather than the primary record. Keep reload and draft restoration explicit so users do not silently lose review work.

## Review Rules

- Prefer reviewability over aggressive auto-correction.
- If OCR meaning is uncertain, make the field easy to inspect and edit rather than guessing.
- Keep extracted value and final value comparable at the same field granularity whenever possible.
- Exclude internal metadata fields from correction comparisons.
- Normalize both OCR and final values before diffing so audit logs do not fill with superficial formatting noise.

## Correction Logging

- Log only reviewer-relevant deltas.
- Include enough provenance to filter later, such as:
  - patient or document identifier
  - OCR model or source
  - extraction timestamp
  - field name
  - original OCR value
  - final reviewed value
- Handle schema drift in the correction log table or file carefully; legacy audit stores often lag behind the current app schema.

## Validation Pattern

- Test one round trip end to end:
  - inject or load OCR seed data
  - render the review form
  - edit a few representative fields
  - save
  - reload
  - verify the final output and correction log
- Include fields that are known to be tricky, such as dates, mutually exclusive radios, split checkboxes, and long free text.
- If the UI reconstructs composite fields from stored atomic values, test both OCR-first and reload-from-storage paths.

## Guardrails

- Do not treat OCR JSON as the long-term source of truth once a reviewed record exists.
- Do not clear the only recoverable OCR or draft state before save succeeds.
- Do not compare raw OCR text directly against saved values when the UI or backend performs normalization.
- Do not hide mapping ambiguity inside silent heuristics if reviewers need traceability.
- Do not let audit logs capture every formatting difference; log semantic corrections.
