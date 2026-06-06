# QR Scanner Order Flow

Use this reference when a printed worksheet, label, or app screen contains a QR payload that can trigger AHK/EMR order actions.

## Payload contract

Use stable ASCII keys so Japanese keyboard layouts, IME state, and EMR text fields do not change the machine-readable part.

Recommended keys:

- `KID`: exam or workflow ID controlled by the app
- `PID`: patient or chart ID used for human cross-checking
- `NAME`: optional patient display name for confirmation screens
- `ADD`: comma-separated order set IDs or command IDs
- `ACT`: action route, such as `set_order`, `print_label`, or a site-specific action

Example shape:

```text
KID:K26060101|PID:2949|NAME:Yamada Taro|ADD:SET_A,SET_B|ACT:set_order
```

Keep site-specific names out of the parser. Map `ACT` and `ADD` values through a configuration table so unsupported values fail visibly.

## Two execution paths

Support both paths during rollout:

- App open: scan into the app quick-find field, parse the QR, show the app confirmation dialog, then launch the one-shot AHK bridge.
- App closed or unfocused: resident `main.ahk` captures the QR prefix/hotkey, parses the payload, shows an AHK confirmation dialog, then calls the same shared order logic.

Both paths must display patient ID, name, exam ID, and order items before execution. The operator must confirm that the correct EMR patient is already open.

## Scanner setup

Validate scanner configuration on each terminal with Notepad before testing the EMR:

- body text appears exactly once
- ASCII punctuation such as `:`, `|`, and `,` is not converted
- suffix Enter is present when the app field expects automatic submission
- prefix function key is present when resident AHK capture is required

Prefer function keys outside common application shortcuts for the AHK capture prefix. Avoid assuming F13/F14 are free; use later function keys only after terminal testing confirms they are unused.

## EMR field behavior

If the QR is scanned while the EMR has focus, the raw payload may remain in an EMR text field. Decide deliberately whether to clear it.

Leaving a short human prefix plus the machine payload can be acceptable during early rollout because it makes wrong-patient or missed-prefix incidents visible. If it becomes noisy, route the scanner through an AHK-only prefix and suppress normal text input after verification.

## Safety rules

- Never execute immediately on scan; always show a confirmation screen first.
- Treat the app record as the source of truth for order intent.
- Treat the EMR as the execution target, with the current open patient as a high-risk assumption.
- Record an audit log entry with terminal ID, exam ID, patient ID, action, order IDs, and success or failure.
- On unsupported `ACT` or `ADD` values, fail before clicking the EMR.

## Go-live checks

- Scan the QR into Notepad and compare to the generated payload.
- Scan into the app field and verify confirmation plus bridge launch.
- Scan while the EMR has focus and verify the resident AHK capture path.
- Confirm the bridge brings the EMR forward only after the operator confirmation.
- Confirm a wrong or unsupported order set is rejected without EMR clicks.
