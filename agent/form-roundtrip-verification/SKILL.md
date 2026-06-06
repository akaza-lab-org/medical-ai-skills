---
name: form-roundtrip-verification
description: Verify end-to-end roundtrip behavior in apps that import or seed data into a form, allow review edits, save normalized records, reload them, and generate downstream outputs. Use when Codex needs to check that create, import, edit, save, reload, history, export, PDF, spreadsheet, or audit-log flows still agree after code or schema changes.
---

# Form Roundtrip Verification

## Overview

Use this skill to confirm that a form-based application preserves intent across its full data journey, not just at the save endpoint.

Prefer one representative round trip with meaningful assertions over many shallow checks.

## Verification Flow

1. Start from a realistic entry path.
   Choose one:
   - blank form create
   - OCR or import seed
   - reload existing record
   Use the path most affected by the recent change.

2. Assert the review form state.
   Check that:
   - the page loads
   - expected fields are present
   - imported or reconstructed values appear in the right controls
   - any highlight, warning, or provenance indicators still show

3. Edit representative fields before save.
   Include at least one field from each risky category:
   - text
   - radio or select
   - boolean checkbox
   - date or split date
   - long free text

4. Save and inspect the response.
   Verify:
   - success status
   - returned record identifier
   - any created history or correction-log metadata

5. Reload through the real read path.
   Do not trust in-memory data.
   Fetch the saved record the same way the UI would and compare the normalized values that matter.

6. Generate at least one downstream output.
   Depending on the app, check:
   - PDF
   - spreadsheet
   - export JSON
   - audit CSV
   - history list
   Confirm the output exists and carries the intended values.

7. Check side effects and persistence.
   If the app writes database rows, files, backups, or logs, confirm the expected artifact was created and is readable.

## What To Assert

- Save returns success and stable identifiers
- Latest-search and history endpoints return the expected record
- Normalized values survive save and reload
- Derived fields are recalculated as expected
- Outputs use the saved final values, not stale draft values
- Audit or correction logs contain semantic changes only when applicable

## Good Test Data

- One record with enough variety to touch risky mappings
- One edited field whose output is easy to assert
- One long text field to expose clipping or wrapping regressions
- One field with normalization behavior such as booleans, enums, or dates

## Guardrails

- Do not stop after a successful save response.
- Do not verify only raw database values if the user interacts through transformed UI fields.
- Do not use toy data that bypasses the tricky branches.
- Do not rely on browser cache or local state when checking reload behavior.
- Do not treat output file existence alone as proof that exported content is correct.
