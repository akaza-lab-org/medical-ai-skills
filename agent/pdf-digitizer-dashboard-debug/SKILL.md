---
name: "pdf-digitizer-dashboard-debug"
description: "Use when debugging the local Flask dashboard and editor launch flow in the `pdf_digitizer` repo, including `/api/state`, task logs, editor processes, and required-path validation."
---

# PDF Digitizer Dashboard Debug

Use this skill for dashboard and local editor launch issues in `pdf_digitizer`.

## Scope
- Dashboard state/API problems
- Editor launch failures
- Wrong project or wrong PDF passed to editors
- Task log and editor log inspection
- Polling, button enable/disable, and required-field UX

## Workflow
1. Start from `dashboard/app.py` and `dashboard/templates/dashboard.html`.
2. Inspect `/api/state` first.
3. If a task failed, inspect `.state/task_logs/`.
4. If an editor failed, inspect in-memory editor logs exposed by the dashboard UI/state.
5. Validate required inputs explicitly:
   - project
   - filled PDF path
   - Phase 2 fields path
   - patient ID for reuse flow
6. Confirm the launched command line matches the selected project and current mode.

## Key files
- `dashboard/app.py`
- `dashboard/templates/dashboard.html`
- `.state/task_logs/`
- `.state/task_artifacts/`

## Practical checks
- Confirm the selected project in dashboard state matches the editor command.
- If a route depends on prior outputs, say so in the UI and in the API error.
- Prefer returning actionable `400` errors over letting spawned editor processes crash.

## Guardrails
- Do not assume the browser error means the route changed; check port, process state, and required inputs first.
- Keep dashboard validation and backend validation aligned.
- If a button depends on repo state, disable it and explain why.
