# Rollout Checklist

Use this reference when introducing new AHK-linked medical workflow features onto already deployed terminals.

## Config and setup

- Verify `setup.ahk` copies every newly added bridge/helper script.
- Verify setup keeps the existing `config.ini`.
- Verify setup backs up `config.ini` before migration.
- Verify migration fills only missing keys.
- Verify migration seeds newly added coordinate keys and hotkey keys.

## Terminal validation

For each terminal type, confirm:

- correct profile is selected by default
- existing coordinates still work after update
- new coordinates appear in the config editor
- direct bridge launch works if required on that terminal
- resident `main.ahk` still starts and registers hotkeys cleanly

## Workflow validation

- Initial order path works end to end.
- Additional order path supports `save only`, `issue now`, and `reissue`.
- Unsupported set IDs fail clearly before or during launch.
- Audit trail records terminal, patient, exam, action, and result.

## High-risk regressions

- `#Warn` from bridge scripts due to main-only handlers leaking into shared libraries
- copied code missing from setup targets
- config editor shows new fields but migration did not seed them on old terminals
- procedure-room staff can launch without first opening the EMR chart
- no visible `pending/unissued` state after a skipped or failed launch