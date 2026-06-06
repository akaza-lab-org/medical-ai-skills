# Tuning Checklist

Use this checklist when the preprocessing output looks wrong or inconsistent.

## Header and Footer Crop

- Increase `header_pt` when repeated page headers still leak into cleaned text.
- Decrease `header_pt` when the first clinical line on each page disappears.
- Increase `footer_pt` when page counters or fixed footers remain.
- Treat the first page separately if it is a cover sheet, referral sheet, or summary page with a different layout.

## Text Cleanup

- Review `raw_kept.txt` before changing line-join heuristics.
- Keep line normalization conservative; aggressive joins can destroy chronology boundaries.
- Remove repeated noise patterns only when they are clearly boilerplate across many pages.

## Date Recovery

- Prefer text-native date extraction before OCR.
- When OCR is needed, crop a narrow region around the expected timestamp anchor instead of OCRing the whole page.
- Save candidate images and OCR variants so false guesses can be audited later.
- Store manual corrections separately and make them traceable by page and candidate index.

## Warning Detection

- Warning tags should flag review targets, not claim certainty.
- Start with broad classes such as facility-like, referral-like, and doctor-like strings.
- Avoid deleting flagged lines automatically unless the repository explicitly requires redaction.

## Validation Pass

- Compare original and cropped preview images on at least the first few pages.
- Read `review.md` before trusting `ready_for_llm.txt`.
- If record count drops unexpectedly after a change, inspect crop settings and date parsing before modifying downstream prompts.
- If no dates are detected, check whether the source document uses image-based timestamps, unusual date formats, or a shifted anchor position.
