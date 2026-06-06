---
name: windows-registered-label-printing
description: Design and implement label printing workflows where a non-lab terminal queues print requests and a lab terminal polls and executes them via Windows-registered LAN printers. Use when direct SDK/raw-protocol access is unavailable, when printing must survive across roles and terminals, or when reprint history and audit trail are required.
---

# windows-registered-label-printing

Use this skill when a medical or operational app needs to send labels to a Windows-registered LAN printer from any terminal, but the printing terminal is different from the requesting terminal (e.g., reception queues a fobt/bag label, lab terminal prints it).

## Core architecture

Split printing into two roles:

- **Requester** (any terminal): POSTs a print request to a queue endpoint. Does not execute printing itself.
- **Executor** (lab/designated terminal): Polls the queue, executes the print job locally, then reports done or failed.

This separation avoids requiring every terminal to have the label printer registered.

## PrintJob model

Minimum fields:

```
id             Integer PK autoincrement
exam_id        ForeignKey → examinations
label_type     String  (fobt / bag / etc.)
status         String  pending → printing → done / failed
requested_terminal  String
requested_at   DateTime server_default=now()
executed_terminal   String nullable
executed_at    DateTime nullable
error_message  String nullable
```

Keep label types validated server-side. Reject unsupported types with 400 before inserting.

## API endpoints

| Method | Path | Role | Purpose |
|--------|------|------|---------|
| POST | `/lab/api/print_request` | any authorized role | queue a job |
| GET | `/lab/api/print_queue` | lab only | fetch pending jobs |
| POST | `/lab/api/print_done/{job_id}` | lab only | mark done or failed |
| GET | `/lab/api/print_history` | lab/control | recent job list |

The executor terminal claims a job by transitioning `pending → printing` before executing, preventing double-execution if two lab tabs are open.

## Printing execution (lab terminal)

Recommended stack when SDK/raw access is unavailable:

1. Rasterize the label PDF to a bitmap via `PyMuPDF` at the target DPI.
2. Send to the Windows-registered printer via `pywin32` (`win32print` / `win32ui`).
3. Keep the preview PDF as a separate artifact; do not send the PDF directly to the printer.

Why bitmap over PDF: PDF rendering through Windows print spooler is driver-dependent and fails silently on narrow-label printers. An image at the correct DPI is stable across drivers.

## Lab page polling

- Poll `/lab/api/print_queue` on a configurable interval (e.g., 5 s) using `setInterval`.
- Show an auto-refresh toggle so operators can pause polling during a busy moment.
- Display pending count in the nav badge or page title to draw attention without a full modal.
- On print completion, refresh the queue and log the result inline.

## Reprint flow

- Add reprint buttons on any page that shows a completed exam.
- A reprint is a new `PrintJob` row — do not mutate the original.
- Show the reprint count on the button if it has been printed before, so operators notice repeated requests.
- Audit-log each print request with `label_type`, `job_id`, and requesting terminal.

## Role and terminal guards

- Only the lab role (or explicitly listed roles) should execute jobs.
- Any authorized role can request printing.
- Store `requested_terminal` from `settings.json` terminal_id at request time so the audit trail is meaningful.

## Error handling

- If the print job fails, set `status=failed` and store `error_message`.
- Show failed jobs in the lab queue with a retry button.
- Alert the operator with both a toast and a dialog for print failures — silent failures in a clinical setting are dangerous.

## Label text scaling for variable-length fields

Medical labels often contain fields whose length varies widely: kanji patient names, furigana readings, 6–7 digit IDs, and long insurance numbers. Fixed font sizes cause overflow or truncation.

Recommended approach — try-and-shrink:

```python
def fit_text(canvas_obj, text, x, y, max_width, font_name, start_size, min_size=6):
    size = start_size
    while size >= min_size:
        canvas_obj.setFont(font_name, size)
        if canvas_obj.stringWidth(text) <= max_width:
            break
        size -= 0.5
    canvas_obj.drawString(x, y, text)
```

Practical rules:
- Set a maximum font size that looks good for typical short names, then shrink in 0.5 pt steps down to a minimum (6–7 pt for narrow labels).
- Apply separate scaling passes for each independent text region (name, furigana, ID) rather than scaling the whole label together.
- For two-line compound fields (furigana above, kanji below), scale each line independently so a long furigana does not shrink a short kanji name.
- After rasterizing to bitmap, verify at the target DPI that the smallest expected text is legible before committing the layout.

Keep a visual regression test: generate labels for a short name, a full-width long name, a 7-digit ID, and a long furigana, and capture the output as reference images or inspect dimensions in tests.

## Common failure patterns

- Executor terminal has the printer registered under a different name than what `settings.json` specifies — validate printer name at startup health check.
- Two lab browser tabs both poll and both pick up the same job — transition to `printing` atomically before executing.
- Reprint request issued from a non-lab terminal leaves the job stuck in `pending` if the lab page is not open — consider a visible pending count in the nav.
- PDF sent directly to the Windows spooler renders at wrong size on narrow-label paper — always rasterize first.
