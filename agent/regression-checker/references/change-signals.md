# Change Signals

Use these signals to spot likely regressions quickly.

## High-Signal Counters

- total cleaned lines
- detected chart entry count
- merged date count
- warning count
- date OCR candidate count
- date OCR guess count

## High-Signal Files

- `review.md`
  Best summary of what changed in one file.

- `warnings.json`
  Fast indicator of shifted text content or masking side effects.

- `cleaned.txt`
  Ground truth for most downstream quality questions.

- `page_###_cropped.png`
  Best artifact for crop regressions.

- `date_ocr_candidates/ocr_results.json`
  Best artifact for OCR date regressions.

## Typical Regression Patterns

- Crop increased slightly and silently removed the first medical line on each page
- New cleanup rule merged unrelated lines
- Warning detector stopped firing because text normalization changed
- OCR candidate region shifted and dates became blank or implausible
