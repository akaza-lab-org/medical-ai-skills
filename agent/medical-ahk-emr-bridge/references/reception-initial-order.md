# Reception Initial Order

Use this reference when the clinic wants the first order to be generated from reception or another designated origin terminal.

## Recommended sequence

1. Confirm or import the reservation into the app.
2. Issue the exam ID inside the app.
3. Print the internal worksheet or examination sheet.
4. Generate QR tied to the exam ID.
5. Execute the initial AHK/EMR order if the site wants reception-side ordering.
6. Mark the order action in app history or audit log.

## Why this pattern is stable

- The app stays authoritative for what was ordered.
- AHK execution stays concentrated on fewer terminals.
- The printed sheet and QR are already aligned with the app record before the patient moves.

## When not to force reception-side ordering

Prefer procedure-room ordering instead if:

- the order printout physically needs to come from a printer beside the procedure room
- the EMR screen must already be open on the active patient in the procedure room
- reception-side ordering creates duplicate handling or extra walking for staff

## Data to persist on initial order

- `exam_id`
- `patient_id`
- selected test set IDs
- terminal ID and terminal role
- issued / failed result
- timestamp

## UI hints

- Use one clear primary action such as `受付確定して初回指示`.
- If AHK launch is optional, still save the app state first and record that ordering was skipped.
- Show a short success summary: printed items, emitted QR, ordered sets.