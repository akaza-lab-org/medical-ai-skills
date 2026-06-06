# Workspace Layout

Use this reference when creating or validating a case-based processing layout.

## Recommended Structure

```text
case_workspaces/
  <case_id>/
    metadata.json
    redaction_rules.json
    inputs/
      pdf/
      notes/
      images/
      labs/
    outputs/
      preprocess/
        <pdf_stem>/
          cleaned.txt
          ready_for_gemini.txt
          warnings.json
          review.md
          ...
```

## File Roles

- `metadata.json`
  Case-level summary and processing settings.

- `redaction_rules.json`
  Case-local masking rules.

- `inputs/*`
  Source artifacts or operator-provided context.

- `outputs/preprocess/<pdf_stem>/`
  All generated artifacts for a specific input PDF.

## Naming Guidance

- Use a slug derived from case name when possible.
- Add a timestamp suffix only to avoid collisions.
- Keep output directory names aligned with PDF stem so debugging is easier.

## Why This Layout Helps

- Makes cases independently reviewable
- Avoids cross-case leakage
- Simplifies dashboard routes and file serving
- Keeps manual corrections close to the artifact they modify
