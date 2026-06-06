---
name: wakumy-safe-snapshot-sync
description: Use when an external reservation or patient system exports recurring full-snapshot CSV files and the app must sync them into a local database without reverting newer data, overwriting manual edits, or losing cancellation state. Covers source ownership, newer-file precedence, reservation-id matching, delayed patient-master updates, and soft-deactivation of cancelled reservations.
---

# Wakumy Safe Snapshot Sync

Use this skill when a local app ingests recurring CSV snapshots from an external reservation or patient system and must keep the database current without unsafe overwrites.

This is most useful when:
- reservation CSV and patient-master CSV are exported separately
- patient-master updates may lag behind reservation exports
- operators sometimes create or edit records manually in the app
- cancelled reservations should disappear from work queues without being hard-deleted
- the external system provides a stable reservation identifier

## Core Rules

1. Separate source ownership.
   Track whether a record is app-managed (`manual`) or CSV-managed (`wakumy` / external sync).
   Do not treat all existing rows as equally safe to overwrite.

2. Store minimal sync metadata.
   For synced records, keep:
   - `last_synced_at`
   - `source_file`
   - `source_kind` such as `reservation` or `patient`
   - external reservation id when available
   This is enough to enforce ordering and debug sync results.

3. Prefer stable external ids over fuzzy matching.
   Match reservations by external reservation id first.
   Only fall back to patient id plus reservation date when no better key exists.

4. Never let older CSVs revert newer data.
   Compare incoming file time against the row's last sync time.
   If the incoming CSV is older, it may fill blanks only; it must not replace newer synced values.

5. Protect manual edits by default.
   For `manual` records, CSV sync should usually fill blanks only.
   Do not overwrite nonblank manual values unless the product explicitly supports operator-approved reconciliation.

6. Allow newer CSVs to update CSV-owned rows.
   For rows whose source ownership is external-sync, a newer CSV may replace nonblank values such as:
   - address
   - phone
   - insurance / member number
   - kana / display name
   - placeholder birth dates
   This keeps the database converging toward the external master.

7. Handle delayed patient-master feeds explicitly.
   Reservation CSV may arrive before patient-master CSV.
   Design for this by allowing reservation imports to create a minimal patient row, then letting a newer patient-master CSV enrich or update that row later.

8. Soft-deactivate cancellations.
   When the external feed marks a reservation as cancelled, do not hard-delete the app row.
   Instead set an active flag such as `is_active = false` and keep the external status.
   Operational screens should filter inactive reservations out.

9. Keep list screens simple.
   Work queues such as reception, control, and doctor lists should only show active reservations for the selected date.
   Historical state can remain in the database for traceability.

10. Keep the sync deterministic.
   Favor explicit ordering rules and field-by-field update policy over heuristics.
   Deterministic sync is easier to test and safer in clinic operations.

11. Handle multiple CSV files in a directory by newest-file-wins deduplication.
   When the external system drops many snapshot files into a single folder (e.g., `current/`), group rows by patient or reservation key, keep only the row from the newest file per key, and discard rows from older files for that key.
   Do not process each file independently in sequence — that risks reverting a newer entry if an older file happens to be processed last.

12. Wrap startup auto-sync behind a feature flag.
   Provide a setting such as `external_sync_startup_enabled` (default `false`) so operators can enable or disable automatic CSV ingestion on app start without code changes.
   When enabled, run the sync during the app lifespan startup event and log the result.
   Always save an audit record regardless of whether sync was triggered by startup or by a manual button.

## Import Audit Record

For each import run, write a row to an audit table or append to a log file:

```
imported_at       DateTime
source_kind       String   (e.g., 'reservation', 'sc_patient_master')
source_file       String
rows_total        Integer
rows_created      Integer
rows_updated      Integer
rows_skipped      Integer
rows_error        Integer
```

This lets operators verify that the last import completed and understand what changed, without reading the DB directly.

## Recommended Data Model Additions

For patient/master rows:
- `sync_source`
- `external_last_synced_at`
- `external_last_source_file`
- `external_last_source_kind`

For reservation/exam rows:
- `sync_source`
- `external_reservation_id`
- `external_reservation_status`
- `external_is_active`
- `external_last_synced_at`
- `external_last_source_file`

Rename the `external_*` fields to fit the target system.

## Recommended Sync Workflow

1. Parse the incoming CSV and record the effective source timestamp.
2. Resolve or create the patient row.
3. Apply patient updates according to ownership and timestamp rules.
4. Resolve or create the reservation row, preferring external reservation id.
5. Merge exam/menu flags without losing already-known positive flags unless the product explicitly wants full replacement.
6. Apply cancellation by setting an active flag false.
7. Save sync metadata.
8. Commit once per import batch unless partial-failure recovery requires smaller transactions.

## Safety Checklist

Before finalizing a sync design, confirm:
- Manual rows cannot be silently overwritten by CSV.
- Older CSVs cannot revert newer synced values.
- Reservation matching does not rely only on patient id + date if a stable external id exists.
- Cancelled reservations disappear from day-to-day queues.
- The app can explain which file last updated a row.
- Tests cover newer-file update, older-file no-op, manual protection, and cancellation handling.

## Good Fit

Use this skill for:
- clinic reservation sync
- patient master enrichment from delayed exports
- repeated full-snapshot CSV imports
- office apps that combine operator edits with external-system snapshots

## Not The Main Fit

Do not use this skill as the main guide for:
- one-time CSV migrations
- append-only event logs
- OCR reconciliation flows
- highly normalized enterprise ETL pipelines with a dedicated warehouse layer

In those cases, use a more specialized migration, OCR, or data-platform skill.

