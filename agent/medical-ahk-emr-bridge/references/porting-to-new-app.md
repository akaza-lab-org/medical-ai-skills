# Porting the App-to-AHK Bridge Pattern

Use this reference when applying the existing medical app + AHK + EMR integration pattern to a different medical workflow app.

## First Questions

Clarify these before designing code:

- Which app owns the workflow state and audit history?
- Which external system or screen does AHK operate?
- Which actions are safe to automate and which must stay manual?
- Which terminal role launches the action?
- Which identifier proves the correct patient or target record is open?
- What is the recovery path when the app state is saved but AHK execution is skipped or fails?

If any answer changes medical safety, fee/order logic, EMR/AHK execution order, production deployment, or destructive data behavior, stop and request Human CTO decision.

## Reusable Architecture

Use this shape by default:

```text
medical app
  owns workflow state, target record, action intent, pending state, audit log
  launches one-shot bridge with structured payload

*_bridge.ahk
  validates payload and terminal config
  performs one action
  exits with clear success/failure code

main.ahk
  remains resident for human hotkeys, palette, manual helpers, and profile switching

EMR / external app
  execution target only
```

Do not make the new app send generic hotkeys to `main.ahk` as the normal integration. Direct bridge launch gives better argument validation, logging, and window-focus safety.

## Payload Design

Use neutral fields for the portable layer, then map them to app-specific names:

- `target_id`: app-specific record ID, visit ID, exam ID, or task ID
- `patient_id`: required when the action can affect a chart
- `display_name`: optional; show to humans before execution, but do not rely on it as the only key
- `action_type`: bridge route name
- `item_ids`: app-specific order, task, document, or command IDs
- `reason`: why this bridge action is being run
- `terminal_id`: optional but useful for audit and config selection
- `raw_payload`: optional QR or scanner input preserved for troubleshooting

Keep action names explicit, such as `kenshin_set_order`, `fobt_result_entry`, or `label_reprint`. Avoid overloaded actions such as `run` or `send`.

## App Responsibilities

The app should:

- validate unsupported `item_ids` before launching AHK when possible
- show patient ID, name, target ID, and requested items before any chart-affecting action
- require explicit confirmation for actions that assume the correct EMR patient is already open
- create an audit record for attempted, succeeded, failed, skipped, and manually recovered actions
- keep a visible pending/unissued state when app changes are not yet reflected in the EMR
- expose a reissue/retry path that does not require editing the database by hand

## AHK Responsibilities

The bridge script should:

- parse only the payload shape it owns
- fail fast on unknown action types or unsupported IDs
- read terminal/profile settings from config, not hard-coded coordinates
- perform one action and exit
- write enough local log detail for support without storing patient identifiers in committed files
- avoid references to callback tables or functions that exist only in `main.ahk`

Keep shared UI operation code in `lib/` only when both `main.ahk` and bridge scripts can load it without side effects.

## Rollout Rules

When introducing the pattern to another app:

- preserve existing manual workflows until the bridge is proven in daily operation
- add any new bridge/helper script to setup or deployment copy targets
- never overwrite tuned `config.ini`; add missing keys through migration
- back up config before migration and restore it if migration fails
- use a dry-run or validation mode before touching EMR screens when possible
- record the rollout result in the relevant GitHub Issue or PR

## Minimal Verification

Before accepting the new app integration:

- app-side command construction tests cover supported and unsupported actions
- bridge validates or dry-runs without requiring `main.ahk` to be resident
- manual `main.ahk` hotkeys still work
- config migration preserves existing terminal values
- skipped or failed execution leaves a visible recovery path in the app
- audit history shows who ran what, from which terminal, for which target record
- no patient data, production logs, screenshots with identifiers, or terminal secrets are committed
