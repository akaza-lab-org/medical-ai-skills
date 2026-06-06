---
name: shared-folder-sqlite-clinic-ops
description: Design and operate a multi-terminal clinic app where SQLite lives on an SMB shared folder, terminals have distinct roles enforced both in UI and backend, and startup health checks, automatic backups, safe settings persistence, optimistic update conflict checks, editor locks, local drafts, and rollout rehearsal checklists are needed. Use when admin-free multi-terminal deployment is required on a host-PC-based shared folder.
---

# shared-folder-sqlite-clinic-ops

Use this skill when a clinic app must run across reception, exam-room, and doctor terminals without admin rights, using SQLite on a Windows SMB/UNC shared folder as the single database.

## SQLite on SMB — journal mode

Never use WAL on a UNC path. WAL requires shared-memory files that SMB does not reliably support, causing lock inconsistencies and silent corruption.

```python
if db_path.startswith("\\\\"):          # UNC / SMB
    cursor.execute("PRAGMA journal_mode=DELETE")
    cursor.execute("PRAGMA synchronous=FULL")
else:                                   # local
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
cursor.execute("PRAGMA busy_timeout=15000")
```

Always set `busy_timeout` to at least 10–15 seconds. Concurrent terminals will queue rather than immediately failing.

## Terminal role enforcement

Store terminal role in `settings.json` on the local terminal (not the shared folder). Enforce the role in two places:

1. **UI layer**: hide or disable menu items and buttons irrelevant to the role.
2. **Backend layer**: guard endpoints with a `require_role()` dependency that reads the local `settings.json`. Do not trust the UI alone.

Typical roles: `reception`, `doctor`, `lab`, `control`, `all` (admin).

If a terminal has no role configured, fail closed — show a setup screen rather than defaulting to full access.

## Startup health check

Run at app startup (lifespan/startup event) and expose results at `/settings/health`:

| Check | What to verify |
|-------|---------------|
| DB reachable | connect and run a lightweight query |
| DB lock acquire | short write transaction to confirm no stuck lock |
| CSV input folder | path exists and is readable |
| Output folder | path exists and is writable |
| Secondary backup dir | path exists (warn-only if missing) |
| Label printer | printer name registered in Windows (warn-only) |

Log warnings to console for missing optional resources. Block startup only for DB failures.

Cache the last report in memory so `/settings/health` is fast without re-running checks on every request.

## Backup strategy

Three tiers:

1. **Automatic daily backup**: triggered on first startup of the day, copies DB to `data/backups/daily/` with a timestamp suffix. Prune old backups to keep N days.
2. **Manual backup**: operator-triggered from settings UI, writes to the same daily folder.
3. **Secondary backup**: copies to a second path (e.g., USB drive or another network share) configured in `settings.json`. Warn if unreachable; do not fail the app.

Keep backup filenames sortable: `kenshin.db.bak-YYYYMMDD_HHMMSS`.

In a shared-folder deployment, only one terminal should run automatic backups. Use a local `backup_owner_enabled` flag or restrict automatic backups to `control` terminals. Reception, doctor, and lab terminals should skip startup and periodic backups.

Use a shared lock file such as `backups/backup.lock` to prevent duplicate backups if two processes start at the same time. If file locking is unavailable, keep the lock best-effort and rely on backup-owner configuration as the primary control.

Create backups with SQLite's backup API rather than copying the live DB file directly:

```python
with sqlite3.connect(src.as_uri() + "?mode=ro", uri=True, timeout=30) as source:
    with sqlite3.connect(tmp, timeout=30) as target:
        source.backup(target)
        target.execute("PRAGMA journal_mode=DELETE")
        target.commit()
tmp.replace(dest)
```

Write a small `backup_status.json` after each run with timestamp, backup path, secondary-copy result, and message. Surface stale or failed backup status in the health check.

Consider three retention classes:

- `daily`: startup/manual backups, keep around 30 generations
- `weekly`: long-lived Monday backup, keep around 26 generations
- `snapshots`: frequent automatic snapshots, keep enough for short-term rollback

## Safe settings persistence

`settings.json` on the shared folder can be read and written by multiple terminals concurrently. Use write-then-rename to avoid partial writes:

1. Write to `settings.json.tmp` on the same volume.
2. `os.replace()` to atomically rename over the target.
3. On Windows, this is atomic within the same volume even over SMB.

Never write directly to `settings.json` from multiple terminals simultaneously without a lock. If locking is impractical, make only the admin terminal write to the shared settings and keep per-terminal overrides in local `settings.json`.

## Per-terminal local settings

Some settings should live on the local terminal only:

- terminal role
- terminal label / display name
- backup owner flag
- label printer name
- local-only paths (e.g., local temp folder)

Store these in a local `settings.json` that takes precedence over shared settings for terminal-specific keys. Never sync terminal-specific keys back to the shared settings file.

## Shared settings split

When a `shared_dir` is configured, split settings into two layers:

- **Local settings**: terminal-specific values such as `terminal_id`, `terminal_label`, `terminal_role`, `backup_owner_enabled`, and per-terminal printers.
- **Shared settings**: clinic-wide values such as output mode, shared printer names, reservation capacities, holidays, and other values that must be identical across terminals.

Persist only an allowlist of shared keys into `{shared_dir}/settings.json`. Keep all other keys in the local settings file. This prevents one terminal from overwriting another terminal's role or printer configuration.

Derive common paths from `shared_dir` instead of asking operators to enter every path:

```text
{shared_dir}/db
{shared_dir}/imports
{shared_dir}/exports
{shared_dir}/settings.json
```

## Provisional patient registration (TMP ID → confirmed ID)

In clinic apps, patients may be registered before their official system ID is known (e.g., ID issued at the counter on the day of the exam). Use a provisional ID to hold the record until the real ID is confirmed.

**ID format**: `TMP{YYYYMMDD}{4-digit-seq}` — sortable, searchable, clearly recognizable as provisional.

**Patient record fields:**

```
patient_id          String   "TMP20260501_0001" or real ID
needs_confirmation  Boolean  true while TMP
sync_source         String   "manual_pending" for TMP, "manual" once confirmed
```

**Registration flow:**

1. At reservation time, if no official ID is known, auto-generate a TMP ID and set `needs_confirmation=true`.
2. Show a visible warning badge ("ID未取得") on any UI card or row that displays a TMP patient.
3. At check-in, detect `needs_confirmation=true` and show a confirmation modal ("本ID追加登録") that explains the step clearly.
4. On confirmation, update `patient_id` to the real ID and set `needs_confirmation=false`.
5. Skip TMP patients in bulk CSV imports — they exist only in the local DB until confirmed.

**Input validation for conflicting entry** (implement at both frontend and backend):

```
# Both patient_id and provisional name/birth entered simultaneously → reject
if patient_id and has_provisional_info:
    raise 400 "Enter ID only, or name/birth only — not both"
```

This is the most common user confusion: the operator searches by ID but also filled in the name fields from a prior attempt. Checking at both layers prevents the wrong patient from being created.

**Exclusions from auto-processes:**

- TMP patients should be excluded from bulk master imports.
- A health check or daily summary can flag `needs_confirmation=true` patients older than N days as stale provisional records.

## Optimistic update conflict checks

Use an explicit revision check for any screen where operators may leave a stale form open:

- reservation move / cancel
- check-in and payment status updates
- doctor note save / finalize
- imported text re-application
- any cross-terminal state transition

Expose a revision in list and detail payloads, usually `updated_at` or a dedicated integer `revision`:

```json
{
  "exam_id": "20260501-001",
  "updated_at": "2026-05-01T09:30:12.123456"
}
```

Send that value back as `expected_updated_at` or `expected_revision` on every write. On the backend, compare it with the current DB row before mutating:

```python
def ensure_not_stale(row, expected_updated_at):
    if not expected_updated_at:
        return
    expected = datetime.fromisoformat(expected_updated_at)
    current = row.updated_at or row.created_at
    if current and current.replace(tzinfo=None) > expected.replace(tzinfo=None):
        raise HTTPException(409, "This record was updated on another terminal. Reload before saving.")
```

Return HTTP 409 and do not partially write. The UI should show a clear "reload latest state" action rather than merging silently.

Do this even when an editor lock exists. Locks reduce accidental simultaneous editing; revision checks prevent stale terminals from overwriting after lock takeover, browser back, sleep/resume, or network delay.

## Doctor/editor lock and local draft pattern

For long-running doctor or reviewer forms, combine three layers:

1. **Local draft** for input-loss prevention.
2. **Shared editor lock** for cross-terminal awareness.
3. **Revision check** for final overwrite prevention.

Recommended DB fields on the work item:

```text
editor_terminal_id
editor_terminal_label
editor_opened_at
editor_heartbeat_at
updated_at or revision
```

Lock workflow:

1. On open, try to claim the lock with the current terminal id and label.
2. While open, send heartbeat every 30-60 seconds.
3. If another terminal owns a fresh lock, show the owner label and keep the second terminal read-only or blocked.
4. Treat a lock as stale after roughly 2-5 minutes without heartbeat.
5. Allow takeover for stale locks, and allow deliberate force takeover only for authorized roles such as `doctor` or `control`.
6. Record takeover, force takeover, and stale-lock events in the audit log.
7. Release the lock on normal close, but never rely on close events as the only release mechanism.

Local draft workflow:

1. Store drafts on the local terminal, not the shared DB, unless cross-terminal recovery becomes a real requirement.
2. Key the draft by work item id and include `terminal_id`, `base_revision`, `saved_at`, and changed fields.
3. Autosave after input pauses or every few seconds.
4. When the same terminal reopens the same work item, offer restore or discard.
5. Delete the draft after successful formal save.
6. Prune old drafts after 7-30 days.

Use shared drafts only as a second phase when doctors frequently move between terminals. Shared drafts are provisional data and must be visually distinct from final saved records.

## Two-lane reception and reservation safety

Assume reception may split into check-in/payment and phone reservation lanes. Keep writes short and deterministic:

- Write reservation changes only on explicit save.
- Re-check slot capacity inside the save transaction or immediately before commit.
- Exclude the current reservation when checking destination slot capacity during a move.
- Use revision checks for reservation move and cancellation.
- Filter inactive/cancelled external reservations from day queues, but keep them for traceability.
- Keep auto-refresh modest, such as 10-30 seconds or after operator actions, to avoid unnecessary shared DB reads.

## Shared settings overwrite protection

When a settings form POSTs all fields simultaneously, `k not in data` checks are useless — every key is always present in the payload. Use `DEFAULT_SETTINGS` comparison instead.

### Problem: full-form submission clobbers existing shared values

A new terminal with no configured printers submits the settings form. Every shared key (printer names, clinic name, etc.) is present in the POST body as an empty string or default value. A naive `shared_file.update(payload)` overwrites the real clinic data with blanks.

### Fix 1 — Skip empty strings in `_save_shared_file()`

When writing shared keys back to the shared file, skip any string value that is empty while the existing value is non-empty:

```python
def _save_shared_file(shared_dir, shared_keys_data, existing_shared):
    merged = dict(existing_shared)
    for key, value in shared_keys_data.items():
        existing_val = merged.get(key)
        if isinstance(value, str) and isinstance(existing_val, str):
            if value == "" and existing_val != "":
                continue           # never blank-out a real value
        merged[key] = value
    # atomic write via tmp + os.replace()
    tmp = shared_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(shared_path)
```

### Fix 2 — Preserve existing shared values on `shared_dir` first-set

When a terminal's `shared_dir` changes (e.g. first setup), the existing shared file already contains correct clinic-wide values. Read them before saving and restore any key that the new payload left at its default:

```python
def _preserve_existing_shared_on_dir_switch(merged, existing_shared):
    for key in SHARED_KEYS:
        if key not in existing_shared:
            continue
        default_val = DEFAULT_SETTINGS.get(key)
        if isinstance(default_val, bool):
            continue               # boolean defaults are intentional
        new_val = merged.get(key)
        existing_val = existing_shared[key]
        if new_val == default_val and existing_val != default_val:
            merged[key] = existing_val   # restore; don't clobber

# In save_settings():
previous_shared_dir = str(current.get("shared_dir") or "").strip()
shared_dir = str(merged.get("shared_dir") or "").strip()
if shared_dir and shared_dir != previous_shared_dir:
    existing_shared = _load_shared_raw(shared_dir)
    _preserve_existing_shared_on_dir_switch(merged, existing_shared)
```

### SHARED_KEYS allowlist

Define an explicit frozenset of keys that belong in the shared file. Everything else stays in the local `settings.json`:

```python
SHARED_KEYS: frozenset = frozenset({
    "exam_ticket_output", "exam_ticket_printer",
    "printer_a4", "printer_a5",
    "clinic_name", "clinic_phone", "director_name", "doctors",
    # ... add clinic-wide-only keys here
})
```

Never include terminal-specific keys (`terminal_id`, `terminal_role`, `backup_owner_enabled`, etc.) in `SHARED_KEYS`.

### Required tests

```python
def test_save_settings_new_shared_dir_preserves_existing_shared_values(tmp_path):
    """Full-form submit with defaults must not overwrite existing shared printer values."""
    ...

def test_save_settings_same_shared_dir_explicit_change_is_applied(tmp_path):
    """An intentional change (non-default value) must still propagate to the shared file."""
    ...

def test_save_shared_file_empty_string_does_not_overwrite_nonempty(tmp_path):
    """Empty string in payload must not blank-out a real existing value."""
    ...
```

## Distributed clock skew detection

In multi-terminal deployments, system clock drift between terminals can cause time-stamped records (appointments, audit logs, optimistic revision checks) to appear out of order or to trigger false conflict rejections. Detecting drift proactively via the shared folder avoids surprises.

### Pattern: shared-folder heartbeat timestamps

Each terminal periodically writes its own UTC timestamp to a small JSON file on the shared folder:

```
{shared_dir}/health_clock/{terminal_id}.json
{"ts_utc": "2026-06-01T09:30:00.123456", "terminal_id": "reception"}
```

On each health check cycle, a terminal reads the other terminals' files and compares timestamps.

### Anti-pattern: comparing ts_utc directly against now

```python
# WRONG — this measures "time since the other terminal last ran a health check",
# not actual clock drift. A terminal that hasn't checked in will always appear
# to have drifted, generating false positives.
their_ts = datetime.fromisoformat(data["ts_utc"])
drift_sec = abs((now - their_ts).total_seconds())
if drift_sec > max_drift_sec:
    return CheckResult(False, f"時刻ずれ検出: {drift_sec:.1f}s")
```

### Correct pattern: mtime window check first

```python
import json
from datetime import datetime, timezone
from pathlib import Path

MAX_DRIFT_SEC = 30          # alert threshold
COMPARISON_WINDOW = MAX_DRIFT_SEC * 3   # skip terminals silent longer than this

def check_clock_skew(shared_dir: Path, my_terminal_id: str) -> CheckResult:
    clock_dir = shared_dir / "health_clock"
    clock_dir.mkdir(parents=True, exist_ok=True)

    # write own timestamp
    my_file = clock_dir / f"{my_terminal_id}.json"
    now = datetime.now(timezone.utc)
    my_file.write_text(
        json.dumps({"ts_utc": now.isoformat(), "terminal_id": my_terminal_id}),
        encoding="utf-8",
    )

    skew_messages = []
    for path in clock_dir.glob("*.json"):
        if path.stem == my_terminal_id:
            continue
        try:
            file_mtime = datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc)
            # skip terminals that haven't written recently — they are offline,
            # not skewed; comparing their stale ts_utc would be a false positive
            if (now - file_mtime).total_seconds() > COMPARISON_WINDOW:
                continue

            data = json.loads(path.read_text(encoding="utf-8"))
            their_ts = datetime.fromisoformat(data["ts_utc"])
            drift_sec = abs((now - their_ts).total_seconds())
            if drift_sec > MAX_DRIFT_SEC:
                skew_messages.append(
                    f"{path.stem}: {drift_sec:.1f}s ずれ"
                )
        except Exception as exc:
            # unreadable file is not a clock-skew alarm;
            # shared-folder access failures are caught elsewhere
            return CheckResult(True, f"時刻チェックスキップ ({path.name}): {exc}")

    if skew_messages:
        return CheckResult(False, "端末間時刻ずれ検出: " + ", ".join(skew_messages))
    return CheckResult(True, "端末間時刻同期OK")
```

### Key rules

- **mtime window before ts_utc comparison**: check whether the peer wrote recently (`mtime` within `max_drift_sec * 3`) before comparing its `ts_utc`. An offline terminal is not a drifted one.
- **comparison_window = max_drift_sec × 3**: this gives two full health-check cycles of slack so a briefly busy terminal is not falsely flagged.
- **Exception path returns `True`**: if the clock file is unreadable, surface it as a skip message, not an alarm. Shared-folder I/O failures are captured by the separate folder-access health check.
- **Write own timestamp before reading peers**: ensures the file exists and is fresh before others compare against it.
- **Do not store drift state in DB**: the shared folder _is_ the coordination medium; avoid a dependency on the DB being reachable just to check clocks.

## Common failure patterns

- WAL mode on SMB causes `.wal` and `.shm` files to accumulate and DB to become unreadable — always detect UNC path and switch to DELETE mode.
- `busy_timeout` not set causes immediate lock errors when two terminals save simultaneously — always configure it.
- Terminal role not enforced in the backend allows a reception terminal to call doctor-only endpoints — always use a backend guard.
- Shared `settings.json` partially written during concurrent save — always use write-then-rename.
- Secondary backup path unmounted silently skips backup without warning — health check should surface this.
- Old backup files fill the shared drive — always prune to a fixed retention window.
- Every terminal runs startup backups — configure exactly one backup owner in shared-folder operation and add a shared backup lock.
- A stale reservation screen overwrites a newer check-in or cancellation — send a revision token with every write and reject stale writes with 409.
- Doctor editor lock is treated as sufficient protection — still enforce revision checks on final save.
- Browser close or PC sleep loses doctor input — keep local drafts and stale-lock takeover behavior.
- Terminal-specific settings leak into shared settings — use an allowlist of shared keys.

## Field rollout rehearsal

Before production use, run a rehearsal with every real terminal role represented:

- Confirm each terminal shows its `terminal_label` and `terminal_role`.
- Confirm no ordinary production terminal is left as `all`.
- Confirm only one terminal is the automatic backup owner.
- Confirm shared folder read/write, DB access, DB lock test, DB integrity check, exports, secondary backup, and printer checks.
- Confirm reception two-lane conflicts: stale reservation move, stale cancellation, and last-slot double booking.
- Confirm doctor editor protection: lock owner display, stale takeover, force takeover audit, local draft restore, and stale final save rejection.
- Confirm backup behavior: startup backup, manual backup from control, secondary copy, and ordinary-terminal denial.
- Confirm fallback procedures for shared-folder loss, printer failure, QR/AHK failure, and temporary paper operation.
