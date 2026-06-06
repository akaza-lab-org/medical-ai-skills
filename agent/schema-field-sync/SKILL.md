---
name: schema-field-sync
description: Keep field definitions aligned across application layers after schema changes. Use when Codex adds, renames, removes, or reclassifies fields that must stay consistent across database columns, API payloads, form inputs, OCR or extraction prompts, coordinate or template definitions, mapping code, exports, and regression checks.
---

# Schema Field Sync

## Overview

Use this skill when a single field change can break multiple layers of an app because names and meanings are duplicated across code, prompts, templates, and exports.

Treat field updates as a synchronization task, not a one-file edit.

## Synchronization Pass

1. Find the canonical field contract.
   Decide what defines the source of truth:
   - field definitions JSON or YAML
   - database schema generator
   - coordinate or template file
   - strongly typed model or dataclass
   If no clear source exists, identify the least derived artifact and work outward from there.

2. Enumerate every layer that depends on the field set.
   Common layers:
   - persisted schema or table columns
   - API request and response payloads
   - form input names
   - mapping code between legacy and current names
   - OCR or extraction prompt keys
   - export templates such as PDF coordinates, spreadsheets, or documents
   - validation and regression scripts

3. Classify the change.
   Distinguish:
   - add new field
   - rename field
   - split one field into several atomic fields
   - merge several fields into one UI control
   - retire field but keep backward compatibility
   The required compatibility work depends on the class of change.

4. Update the canonical definition first, then regenerate or reconcile derived artifacts.
   Prefer generation over hand-editing where scripts already exist.

5. Patch explicit compatibility code next.
   Review:
   - legacy alias maps
   - normalization helpers
   - DB-to-form and form-to-DB transforms
   - import and export adapters

6. Compare field sets across layers.
   Run or write comparisons for:
   - canonical definitions vs database columns
   - canonical definitions vs coordinate or template field IDs
   - canonical definitions vs prompt or OCR output keys
   - canonical definitions vs rendered form inputs

7. Test one real end-to-end path.
   A field is not synchronized until create, save, reload, export, and any extraction flow all agree.

## Practical Rules

- Keep field IDs stable when possible; renames are expensive.
- If the UI uses composite controls, document how atomic storage fields reconstruct the composite value and split back on save.
- If output templates use the same field IDs as storage, protect that invariant because it removes whole classes of mapping bugs.
- When backward compatibility is needed, prefer explicit alias maps over hidden fallback behavior.
- Quote or escape problematic field names consistently in SQL, templates, and exports if naming rules are imperfect.

## Change Checklist

- Canonical definition updated
- Database schema updated or regenerated
- Migration or `ALTER TABLE` path handled
- Save mapping updated
- Reload mapping updated
- Form names and defaults updated
- OCR or extraction prompt keys updated
- Output template or coordinate IDs updated
- Export and import paths updated
- Schema comparison checks updated
- Representative tests or verification scripts updated

## Guardrails

- Do not change only the UI label when the storage meaning changed.
- Do not hand-patch one generated artifact and forget its generator.
- Do not assume matching field counts means matching semantics.
- Do not remove legacy alias handling until old stored records, prompts, or imports are proven clean.
- Do not trust a single happy-path save test; reload and output generation often reveal the missing sync step.
