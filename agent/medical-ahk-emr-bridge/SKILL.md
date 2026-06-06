---
name: medical-ahk-emr-bridge
description: Bridge a local medical workflow app to an existing AutoHotkey automation stack and EMR screens without breaking per-terminal config.ini deployments. Use when adding app/QR-triggered AHK actions, splitting resident main.ahk from one-shot bridge scripts, designing safe order-issuance flows where the app is the source of truth and the EMR is the execution target, or porting the same app-to-AHK bridge pattern into another medical workflow app.
---

# medical-ahk-emr-bridge

Use this skill when a local medical workflow app needs to cooperate with an existing AHK automation base that already drives an EMR or order-entry screen.

Use `ahk-legacy-automation` together with this skill when you need low-level AHK reliability patterns, encoding rules, or UI wait/click behavior.

## When to open references

- For reception-side initial order design, read [references/reception-initial-order.md](references/reception-initial-order.md).
- For procedure-room additional-order and unissued-recovery flows, read [references/procedure-room-additional-order.md](references/procedure-room-additional-order.md).
- For QR scanner triggered app/AHK order flows, read [references/qr-scanner-order-flow.md](references/qr-scanner-order-flow.md).
- For porting this bridge pattern into another medical app, read [references/porting-to-new-app.md](references/porting-to-new-app.md).
- For rollout, terminal update, and go-live checks, read [references/rollout-checklist.md](references/rollout-checklist.md).

## Core architecture

- Treat the medical app as the **source of truth** for workflow state, selected tests, and audit history.
- Treat the EMR as the **execution target**. Do not let EMR-only edits become the normal path if they can drift from the app state.
- Split AHK entrypoints into two roles:
  - `main.ahk`: resident, human-facing, hotkeys, palette, profile switching.
  - `*_bridge.ahk`: non-resident, single-run, CLI-driven, app or QR integration.
- Put shared click/order logic in `lib/`. Keep `main.ahk`-only callback tables and hotkey handlers out of shared libs.

## Safe rollout rules

When adding new automation to a deployed AHK environment:

- Keep existing `config.ini` values. Never replace a tuned file with a fresh template.
- Add a migration path such as `UpgradeConfigFileToCurrent()` that only fills missing keys.
- Back up the target `config.ini` before migration, ideally into `backups/` under the install directory.
- If migration fails, restore the backup immediately.
- When adding a new helper or bridge script, also add it to `setup.ahk` copy targets so updated terminals do not silently miss the feature.
- Assume `config.ini` is UTF-16LE when it contains Japanese keys and is used via `IniRead`/`IniWrite`.

## Terminal and profile strategy

- Use per-profile coordinates for shared doctor-room terminals.
- Keep reception and procedure-room terminals on one default profile unless a real variation exists.
- It is fine to have extra profiles available if only one is normally active on a terminal.
- Store terminal-facing settings in config, not in code:
  - coordinates
  - printer names
  - hotkeys
  - enabled profiles
  - terminal labels or roles if the script needs them

## App-to-AHK integration pattern

Prefer direct bridge launch over synthetic key sending when the caller is an app or QR flow.

Use the same pattern when adapting the integration to a second medical app:

- Make the new app the source of truth for its own workflow state, execution intent, pending/unissued status, and audit trail.
- Reuse the resident-vs-bridge split instead of coupling the new app to hotkeys in `main.ahk`.
- Define an app-specific payload schema and action names; avoid copying kensin-specific exam or order-set names unless the workflow really matches.
- Preserve local manual operation paths while the new app is being introduced.

Recommended payload fields:

- `request_id`
- `exam_id`
- `patient_id`
- `order_set_ids`
- `action_type`
- `reason`
- optional `terminal_id`

Recommended behavior:

- App generates a stable `request_id` for each intended execution and records it before launch.
- App validates unsupported order-set IDs before launch when possible.
- Bridge performs one action, writes an outcome status file, and exits with a clear success/failure code.
- Manual operators can still use hotkeys or palette actions from `main.ahk`.
- Keep both paths available when requirements are still changing:
  - manual: hotkey / palette
  - integrated: direct bridge launch

## Request status file pattern

Use a request status file when the app launches AHK asynchronously or when the operator needs a visible recovery path after a one-shot bridge exits.

Pattern:

- The app creates and stores a unique `request_id` before launching AHK.
- The app passes `--request-id <request_id>` or an equivalent CLI argument to the bridge script.
- The bridge writes one status file on every terminal outcome: success, failure, or operator cancel.
- The app polls or reloads the status file and reflects the outcome into its own audit/history model.
- The app treats missing or stale status as pending/unknown, not as success.

Recommended JSON shape:

```json
{
  "request_id": "...",
  "status": "success | failed | canceled",
  "exit_code": 0,
  "message": "...",
  "timestamp": "..."
}
```

Guardrails:

- Do not let the status file become the source of truth. It is an execution receipt; the app remains the workflow and audit authority.
- Include enough information in app-side logs to correlate `request_id`, patient/exam/work item, operator, terminal, and action.
- Write failure and cancel status files deliberately so operators can distinguish "not yet checked" from "bridge failed".
- Use `request_id` for idempotency checks before reissuing orders or retrying a bridge action.
- Keep status paths local and predictable, but do not write patient identifiers into filenames.

For QR scanner flows, prefer an ASCII key-value payload such as:

- `KID:<exam_id>`
- `PID:<patient_id>`
- `NAME:<display_name>` when the QR will be shown to humans before execution
- `ADD:<comma-separated order_set_ids>`
- `ACT:<action_name>`

Use `ACT:` to route one scanner and resident AHK script across multiple workflows. Keep the parser tolerant of both `|` separated and scanner-prefixed text if the EMR field may receive the raw scan.

## Medical order workflow guardrails

Use these defaults unless the site has a stronger existing rule:

- Initial order:
  - run from the reception or other designated origin terminal
  - print or queue required paperwork in the normal clinic flow
- Additional order:
  - edit in the app first
  - then execute the EMR order from the same terminal that has the patient open
- If the operator saves the app change without executing the EMR order, keep an explicit `pending/unissued` state and a reissue path.

For additional orders, require a visible reminder before launch:

- open the correct patient in the EMR first
- executing on the wrong patient can send orders to the wrong chart
- show patient name, patient ID, exam ID, and the new items being added
- require an explicit confirmation checkbox before running AHK

## AHK execution history in the app UI

Surface a compact history strip in the app editor so operators can confirm what was already issued for the current exam without switching to a log page.

Implementation pattern:
- Load from the audit log endpoint with `action=ahk_order` and `target={exam_id}` filters, limited to 5 entries.
- Render inline as a small muted strip: `{time} {action_label} ({terminal_id})`.
- Show a neutral placeholder when no history exists rather than hiding the element — helps distinguish "not yet run" from a failed load.
- Populate on exam open and after each successful bridge launch.
- Do not block the editor load if the history fetch fails; degrade silently with a low-opacity fallback.

Keep unsupported order-set IDs visually distinct (e.g., red highlight) in the same section so operators know before confirming which items will be rejected.

## Common failure patterns

Watch for these issues:

- bridge script includes a shared handler table that references functions only defined in `main.ahk`, causing `#Warn` or missing-symbol behavior
- setup updates copy new code but leave out the new bridge/helper file
- coordinates are added in the editor UI but not seeded into migration defaults, so older terminals miss them
- app launches a generic hotkey send instead of a dedicated bridge path and loses window-focus safety
- staff adds orders in the EMR only and forgets to reflect them in the app

## Verification checklist

After implementing a bridge flow, verify all of the following:

- existing terminals can run setup update without losing `config.ini`
- newly added config keys appear on upgraded terminals
- resident `main.ahk` still works for manual hotkeys and palette
- bridge script can run without `main.ahk` already resident, unless the design explicitly requires otherwise
- bridge writes a status file for success, failure, and operator cancel paths
- app displays pending/unknown status when the expected status file is missing or stale
- unsupported order-set IDs fail clearly
- procedure-room flow works only after opening the intended patient in the EMR
- app can show `pending/unissued` and reissue additional orders
- audit trail records who ran what, from which terminal, and for which patient/exam
