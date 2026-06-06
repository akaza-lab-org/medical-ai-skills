# Review Checklist

Use this checklist after applying PHI masking rules.

## Before Applying Rules

- Confirm which files are canonical source artifacts.
- Confirm which files are safe to regenerate.
- Confirm whether the redacted output is intended for internal review, external sharing, or LLM ingestion.

## After Applying Rules

- Read the beginning, middle, and end of `redacted_cleaned.txt`.
- Read the prompt-ready redacted derivative to ensure chronology and medical meaning still make sense.
- Inspect `redaction_warnings.json` for surviving facility names, physician names, referral markers, or suspicious residual text.
- Compare with the original warning output if the warning count changed dramatically.

## Residual PHI Questions

- Are patient names fully masked, including OCR variants and shortened forms?
- Are staff names and facility names masked to the intended level?
- Are IDs, dates of birth, addresses, phone numbers, and free-text identifiers still present?
- Did masking accidentally expose identity through context, such as rare workplace or family details?

## Quality Questions

- Did any replacement break sentence readability or chronology grouping?
- Did blank replacement create confusing double spaces or damaged headings?
- Did a shared rule remove medically meaningful terminology in unrelated cases?

## Release Rule

If the output still contains meaningful identifiers or the reviewer is unsure, stop and add or narrow rules before sending the text to another model or another person.
