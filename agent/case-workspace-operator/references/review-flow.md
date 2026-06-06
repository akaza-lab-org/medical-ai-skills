# Review Flow

Use this checklist when operating a case workspace.

## Intake

- Create a new case folder.
- Copy or upload source PDFs into `inputs/pdf`.
- Add supporting notes, images, and lab artifacts to their matching folders.

## Processing

- Run preprocessing against the PDFs inside the case folder.
- Save processing settings in `metadata.json`.
- Ensure the output directory is recorded for later review.

## Review

- Open `review.md` and `warnings.json` first.
- Read `cleaned.txt` and the prompt-ready derivative.
- Check preview images if crop settings or missing text are suspected.
- Review OCR candidate images and manual corrections if dates look wrong.

## Follow-up

- Add or adjust local redaction rules as needed.
- Regenerate redacted derivatives after rule changes.
- Keep all resulting files within the same case workspace.
