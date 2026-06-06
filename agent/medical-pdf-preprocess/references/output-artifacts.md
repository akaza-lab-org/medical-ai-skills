# Output Artifacts

Use this reference when designing, reviewing, or validating a medical PDF preprocessing pipeline.

## Recommended Output Set

- `cleaned.txt`
  Canonical plain-text output after crop-based cleanup and line normalization.

- `ready_for_llm.txt` or `ready_for_gemini.txt`
  Draft prompt payload grouped by detected record date when possible.
  Keep this derivative separate from `cleaned.txt`.

- `warnings.json`
  Machine-readable list of suspicious lines that deserve human review.
  Include line number, tags, and source text.

- `review.md`
  Human-readable summary of crop settings, detected record counts, OCR candidates, OCR guesses, warnings, and removed blocks.

- `raw_kept.txt`
  Text dump before later formatting transforms.
  Useful when record splitting or line joining introduced regressions.

- `blocks.tsv`
  Block-level geometry for debugging missing text or over-aggressive crop settings.

- `records.json`
  Structured run metadata such as source file, crop settings, detected records, merged dates, warnings, and OCR suggestions.

- `page_###_original.png`
  Page preview before crop.

- `page_###_cropped.png`
  Page preview after crop.

- `cropped.pdf`
  Optional convenience artifact for human review.

- `date_ocr_candidates/candidates.json`
  Metadata for each date-region OCR crop.

- `date_ocr_candidates/ocr_results.json`
  OCR guesses, confidence, and source variant for each candidate.

- `date_ocr_candidates/manual_corrections.json`
  Human-confirmed corrections stored without destroying original OCR guesses.

## Minimum Review Questions

- Did crop settings remove only page furniture, not medical content?
- Does `cleaned.txt` still contain the clinically important timeline?
- Does the LLM-ready file preserve chronology and grouping?
- Are warning lines actually risky, or is the tagger too noisy?
- Are OCR date guesses believable enough to merge records?
- If dates are missing, is the problem extraction, OCR, or document quality?

## Artifact Contract

If you reimplement the pipeline in another project, keep filenames and semantics stable when possible.
Stable artifacts make it easier to compare runs, build dashboards, and reuse downstream automation.
