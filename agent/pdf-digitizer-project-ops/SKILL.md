---
name: "pdf-digitizer-project-ops"
description: "Use when working in the `pdf_digitizer` repo on project creation, project reopening, active project switching, manifest inspection, or file layout issues under `projects/` and `.state/`."
---

# PDF Digitizer Project Ops

Use this skill for manifest-backed project setup and selection in `pdf_digitizer`.

## Decision flow
1. Resolve the target project by `project_dir`, not display name.
2. If the task starts from a blank PDF:
   - without an explicit project, create a unique slugged directory under `projects/`
   - with an explicit project or folder, reuse that exact directory and refresh its manifest
3. Read `manifest.json` before assuming file locations. Treat `workflow/project_manifest.py` defaults plus `manifest.paths` overrides as the path source of truth.
4. Preserve `created_at` when reinitializing an existing project, and update `updated_at` when rewriting the manifest.
5. After create, open, or activate flows, verify `.state/active_project.txt` and API payloads point at the same `project_dir`.
6. In dashboard work, return and consume `active_project` plus the full project payload so Phase 1, Phase 2, and Phase 3 actions retarget immediately.
7. Before downstream work, confirm required files from the manifest context, especially `source/form.pdf`, `phase1/initial_fields.json`, and `phase2/edited_fields.xlsx`.

## File anchors
- `workflow/project_manifest.py`
- `dashboard/app.py`
- `dashboard/templates/dashboard.html`
- `.state/active_project.txt`

## Guardrails
- Do not key selection state by `project_name`.
- Do not invent path conventions outside manifest defaults and overrides.
- If the active project lives outside the repo project list, surface it explicitly instead of dropping it.
