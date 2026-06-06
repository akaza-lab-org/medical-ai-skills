---
name: medical-case-app-patterns
description: Reuse the design patterns learned in this repository when building another local medical review, extraction, or webform-assist app. Use when Codex needs guidance on case-based workspace structure, PHI-safe preprocessing, local-vs-LLM separation, Gemini extraction design, review UI flow, deterministic rule layers, file-backed autosave, or portable Windows deployment for clinical workflows.
---

# Medical Case App Patterns

Prefer inspectable, case-based, file-backed workflows over opaque app state.

This skill captures the reusable patterns that worked well in this repository and should be considered first in future medical review or extraction apps.

## Core Patterns

1. Separate source, canonical, and derived artifacts.
   Keep inputs under a case folder.
   Keep canonical extracted text stable.
   Regenerate redacted, corrected, and Gemini-facing outputs from JSON-backed review state instead of hand-editing generated files.

2. Use one case per folder.
   Prefer:
   - `case_workspaces/<case_id>/inputs/...`
   - `case_workspaces/<case_id>/outputs/preprocess/...`
   - `case_workspaces/<case_id>/outputs/extraction/...`
   - `metadata.json` at case root
   This keeps intake, review, re-run, and portability manageable.

3. Keep PHI-local information separate from LLM-bound bundles.
   If cover sheets, patient identifiers, furigana, or local OCR regions are useful, extract them locally and save them as sidecar JSON or text.
   Do not automatically include them in Gemini bundles.

4. Prefer reviewable intermediate artifacts.
   Always expose:
   - cleaned text
   - Gemini-ready text
   - warnings
   - preview images
   - OCR candidates or local extraction summaries
   - extraction validation reports
   This makes failures diagnosable by humans.

5. Prefer structured LLM output over fragile fixed-column TSV when output size or sparsity is high.
   Use JSON schema output for sparse, partially missing clinical fields.
   Allow blanks explicitly.
   Add a normalization step after LLM output to map aliases and common shorthand into application values.

6. Distinguish missing from broken.
   In validation, treat absent real-world information as allowed missing data.
   Reserve errors for structural failure, impossible values, or format drift.

7. Add deterministic post-processing after LLM extraction.
   Normalize common shorthand such as:
   - `1` / `0` -> `yes` / `no`
   - `2` -> `type2`
   - stage aliases -> canonical nephropathy labels
   Let the LLM draft; let code make field values app-safe.

8. Keep human review as a first-class stage.
   Show:
   - extracted value
   - final value
   - source
   - comment
   - optional derived/internal values
   This lets users correct safely without losing machine extraction context.

9. Store app state in visible files, not browser-only storage.
   Use server-backed JSON under a known folder such as `case_manager_data/`.
   Browser `localStorage` is acceptable only as fallback.
   The main saved state should be syncable across PCs by copying a folder.

10. Build small bridges between tools.
   Prefer direct links and handoff files between:
   - preprocess dashboard
   - extraction runner
   - case manager
   - webform filler
   Good bridges include:
   - import buttons
   - explicit run buttons
   - latest-run manifests
   - links back to source review screens

11. Surface execution status explicitly.
   For LLM runs, write status JSON and keep:
   - command
   - model
   - stdout/stderr
   - validation report
   - response metadata
   Do not silently treat empty model output as success.

12. Treat rule automation as a separate deterministic layer.
   Keep domain rules in CSV/JSON or another operator-editable format.
   Apply them after extraction, not inside prompt logic alone.
   Preserve manual overrides.

13. Prepare for portable Windows deployment early.
   Prefer:
   - relative paths from app root
   - file-backed state
   - explicit static/template discovery
   - `.bat` launchers
   - `PyInstaller onedir` over fragile onefile builds
   Aim for "folder copy to another PC" rather than install-heavy deployment.

## Recommended Workflow For A New App

1. Define the case folder contract first.
2. Define canonical artifacts and derived artifacts separately.
3. Decide which information stays local-only and which may go to the model.
4. Build the review screen before optimizing automation.
5. Use JSON schema extraction if blanks and partial data are common.
6. Add deterministic normalization and rule layers after extraction.
7. Add validation reports before bulk usage.
8. Add bridges between tools so users never wonder "what do I run next?"
9. Only then optimize portable packaging and one-click launch.

## Design Smells

- LLM-ready files overwrite canonical cleaned text
- PHI-heavy cover-sheet data is silently bundled to Gemini
- Browser-only saves are the main state store
- Fixed TSV output is used even though many fields are often blank
- Missing data is treated as a hard validation failure
- Reviewers cannot see extracted vs final values separately
- Tool transitions require undocumented manual file hunting
- Portable builds depend on hidden absolute paths

## Fast Heuristics

- If the user says "we may continue on another PC", move state to visible files.
- If the user says "fields are often blank", prefer JSON schema extraction.
- If the user says "PHI must stay local", split local enrichment from Gemini bundle generation.
- If the user says "the last step is a web form", treat extraction JSON as an intermediate product, not the final UI.
- If the user says "we will manually finish the last 10%", optimize for reviewability over full automation.

## Related Skills

This skill covers **what to build** (case folder layout, PHI separation, review flow, deterministic rules).
For **how to call Gemini** from such an app, defer to companion skills:

- `vertex-ai-gemini-medical-app` — Vertex AI (`@google/genai` with `vertexai: true`) initialization,
  current Gemini model IDs (3.5 / 3.1 / 3.0 / 2.5), region constraints (global / us / eu vs asia-northeast1),
  ADC auth, Server Action patterns with `inlineData`, troubleshooting `Publisher Model ... was not found`.
  Use when the app code actually issues Gemini calls — not when designing the case folder contract.
- `claude-api` — Anthropic / OpenAI SDK if the project later swaps providers; this skill should NOT
  apply to Vertex projects.

Pattern: design the case workspace and review flow with `medical-case-app-patterns`, then implement
the LLM call layer with the provider-specific skill. Keep the two concerns separated in code so the
LLM provider can be swapped without rewriting the case workflow.
