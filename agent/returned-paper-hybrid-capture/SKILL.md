---
name: returned-paper-hybrid-capture
description: Design workflows where the app prints or prepares a paper form first, then later re-imports only the handwritten or externally completed regions after the paper is returned. Use when Codex needs to split a document into machine-generated and human-completed sections, add page or QR metadata for later matching, crop target regions from scans, run OCR or multimodal extraction on only those regions, and require a final human verification step before saving results.
---

# Returned Paper Hybrid Capture

Use this skill for forms that leave the system, get handwritten or externally completed, and then come back for partial re-entry.

Treat these flows as hybrid by design. The safe target is not full automation; it is reliable assisted re-capture with explicit human review.

## Good Fit

Use this pattern when most of these are true:

- the app can generate part of the form before submission
- another party completes later fields by hand
- only a subset of the returned form needs to be read back
- scanning the whole page is possible, but only some regions matter
- matching the returned page to the original record matters

If the returned document is fully typed and digitally available, prefer a normal import workflow instead.

## Document Split

Separate the form into these zones early:

- machine-generated section
- handwritten or externally completed section
- regions that must remain blank for paper workflow
- page identity metadata area

Do not design the first release as if all regions will be re-imported later. Choose the minimum high-value region set.

## Workflow

1. Define the first-pass automation boundary.
   Decide which fields the system fills before submission and which fields are intentionally left for later paper completion.

2. Add durable page identity markers.
   Embed enough metadata to match a returned page safely:
   - page number
   - total pages
   - document tag or batch tag
   - QR payload or similar machine-readable token

3. Preserve the original machine-generated state.
   Keep the structured values used to create the outbound form. The returned capture should enrich or complete that record, not replace its provenance.

4. Scope scanning to target regions.
   Crop only the zones that matter for re-import:
   - handwritten judgments
   - secondary interpretations
   - stamped outcomes
   - signatures, only if required
   This reduces noise and lowers OCR or multimodal extraction risk.

5. Extract into review-ready fields, not directly into the final record.
   Store:
   - raw cropped image or reference
   - extraction result
   - confidence or ambiguity markers if available
   - reviewed final value

6. Reconcile with the original record.
   Apply the extracted values to the matching record only after:
   - page identity is confirmed
   - the target region mapping is correct
   - a human confirms the interpreted result

7. Keep a visible final check.
   The operator should be able to compare:
   - original outbound record
   - cropped returned region
   - extracted candidate value
   - final confirmed saved value

## Region Strategy

- Prefer named regions over ad hoc coordinates.
- Keep region definitions versioned with the form template.
- If only one subsection changes each year, isolate that region rather than rebuilding the whole pipeline.
- Use the smallest crop that preserves context needed for interpretation.

## Extraction Strategy

- Use deterministic OCR when the handwriting or marks are constrained and regular.
- Use multimodal extraction when the region includes mixed handwriting, marks, stamps, or awkward layouts.
- Keep the model output narrow:
  - one field
  - one enum
  - one date
  - one short judgment block
  Avoid asking one pass to decode the whole returned form unless the layout is extremely simple.

## Matching And Safety

- Match returned pages using embedded metadata first, not filename guesswork.
- If metadata match and visual content disagree, stop and surface the ambiguity.
- Keep a way to re-open the source cropped image during review.
- Preserve enough provenance to audit later which value came from the returned paper flow.

## Validation Checklist

- print or generate a sample outbound form
- confirm QR or page markers survive print and scan
- scan a returned sample and crop the intended regions
- verify extraction on representative good and messy samples
- verify the correct original record is selected
- verify the operator can confirm or correct before save
- verify the saved value can be traced back to the scanned region

## Guardrails

- Do not attempt full-page automatic ingestion first if only one region matters.
- Do not overwrite outbound structured values with unreviewed extraction output.
- Do not depend on filenames alone to match returned pages.
- Do not hide ambiguity when the scan quality or handwriting is poor.
- Do not skip the final human check for clinically or operationally important fields.
