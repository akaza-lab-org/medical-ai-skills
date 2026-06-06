---
name: case-review-refresh
description: Refresh and verify case-level derived artifacts after manual review changes in this medical PDF preprocessing repo. Use when Codex updates or checks date OCR confirmations, manual text corrections, redaction rules, date privacy options, chronology reconstruction, warning review behavior, or any dashboard action that should regenerate `corrected_*` and `redacted_*` outputs inside a case workspace preprocess output folder.
---

# Case Review Refresh

Treat the dashboard review flow as a regeneration workflow, not a hand-edit workflow.

Preserve canonical outputs and regenerate derived artifacts from disk-backed state.

## Workflow

1. Identify the case and preprocess folder.
   Prefer the active case workspace under `case_workspaces/<case_id>/`.
   Confirm which `outputs/preprocess/<pdf_stem>/` folder the dashboard is showing.

2. Read the stored review inputs before changing code.
   Inspect only the files relevant to the requested behavior:
   - `date_ocr_candidates/manual_corrections.json`
   - `manual_text_corrections.json`
   - `redaction_rules.json`
   - `date_privacy_config.json`
   - `warnings.json`
   - `boundary_alerts.json`

3. Regenerate, do not hand-edit.
   Prefer calling the same Python functions or POST routes the dashboard uses.
   Treat these outputs as derived and refresh them together:
   - `corrected_cleaned.txt`
   - `corrected_ready_for_gemini.txt`
   - `corrected_warnings.json`
   - `redacted_cleaned.txt`
   - `redacted_ready_for_gemini.txt`
   - `redaction_warnings.json`
   - `date_privacy_map.json`

4. Verify the downstream artifact that matters.
   If the change affects Gemini understanding, inspect `redacted_ready_for_gemini.txt`.
   If the change affects chronology, inspect section headings and record ordering.
   If the change affects review usability, inspect the case detail template and related JSON files.

5. Report exact files and whether regeneration happened.
   Mention if you only changed code and did not re-run regeneration for a representative case.

## Decision Rules

- Keep `cleaned.txt` and the original preprocess artifacts untouched unless the core preprocessing itself changed.
- Apply shared redaction rules first, then case-local rules, then date privacy masking on the Gemini-facing redacted output.
- When chronology is rebuilt from confirmed dates, verify left-column text stays ahead of right-column text across page breaks.
- If Japanese text looks broken in terminal output, use `$text-encoding-guard` before deciding the file is corrupted.
- If a dashboard save appears ineffective, inspect the JSON source of truth first, then verify the regenerated derived files.

## Fast Checks

- Run `python -m py_compile preprocess_dashboard.py preprocess_pdf.py` after Python changes.
- Use `rg` against the target output file to confirm important replacements or headings.
- For representative cases, inspect at least one `redacted_ready_for_gemini.txt` and one review JSON file after regeneration.
