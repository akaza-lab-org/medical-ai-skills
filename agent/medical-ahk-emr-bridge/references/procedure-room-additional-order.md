# Procedure Room Additional Order

Use this reference when additional orders are usually entered from the same terminal where staff is already working in the procedure room.

## Default rule

Treat `app edit = order intent`, but keep a recoverable `pending/unissued` state for exceptions.

## Recommended flow

1. Open the patient in the EMR first.
2. Open the same patient in the app by QR, exam ID, or patient ID.
3. Edit the requested additional items in the app.
4. Offer two actions:
   - `保存のみ`
   - `保存して追加指示発行`
5. Before running AHK, show a confirmation dialog with:
   - patient name
   - patient ID
   - exam ID
   - new items being added
   - required checkbox confirming the correct EMR chart is open
6. Run the bridge.
7. Save result as `done` or `failed`.

## Required recovery path

If staff saves changes but does not run the EMR order:

- leave an explicit `pending/unissued` state
- show an `未発行` badge in lists or detail panes
- provide `未発行の追加指示を発行` or `再発行`

## Why this matters

This avoids the failure mode where:

- staff modifies the EMR only
- the app record is left stale
- later PDF, billing, or audit outputs disagree with the real action

## Safety reminder text

Use wording close to this before launch:

- Open the correct patient in the EMR before running.
- If another patient is open, the order may be sent to the wrong chart.