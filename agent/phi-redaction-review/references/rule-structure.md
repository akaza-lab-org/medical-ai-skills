# Rule Structure

Use this reference when implementing or reviewing PHI masking rules.

## Recommended Rule Files

- `shared_redaction_rules.json`
  Global substitutions that recur across many cases or many projects.

- `<case>/redaction_rules.json`
  Case-local substitutions for patient names, referring facilities, staff names, identifiers, or one-off spelling variants.

## Recommended JSON Shape

```json
[
  {
    "target": "Original string",
    "replacement": "Alias or blank"
  }
]
```

Keep the structure simple unless the project truly needs regex metadata or rule activation flags.

## Scope Guidance

- Put common physician or facility aliases in shared rules only after verifying they are safe across cases.
- Keep patient-specific names, chart numbers, and one-off OCR variants in local rules.
- If a target appears in both scopes, let the local rule effectively represent the final intended behavior.

## Regeneration Pattern

Recommended derived files:

- `redacted_cleaned.txt`
- `redacted_ready_for_llm.txt` or `redacted_ready_for_gemini.txt`
- `redaction_warnings.json`

Generate them from the canonical unredacted artifacts every time rules change.

## Common Risks

- Very short targets such as one-kanji surnames or initials can overmask unrelated content.
- Facility names can contain department names that also appear in legitimate clinical text.
- OCR noise can produce near-matches that require separate local rules instead of one broad shared rule.
