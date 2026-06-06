# File Recovery Checklist

Use this reference when the file content itself is already corrupted.

## First Questions

- Is the source of truth still available in git, a backup, or another file?
- Did the corruption happen on read, on write, or during copy/paste?
- Is the damage local to UI strings, or does it affect structured data too?

## Recovery Order

1. Recover from a clean source if possible
2. If only a small text block is damaged, rewrite that block from trusted content
3. If many labels are damaged, rewrite the file or section wholesale
4. Re-check with explicit UTF-8 reads

## Practical Guidance

- HTML templates with many broken labels are often faster to rewrite cleanly
- Markdown and README files are usually safe to regenerate from trusted text
- JSON should be re-read after writing to confirm structural validity and readable text
- Python source with corrupted string literals should be verified with `py_compile` after repair

## Validation Pass

- Search for mojibake fragments such as `繧`, `縺`, `蜑`, `逞`, or replacement characters
- Re-open the file with explicit UTF-8 reads
- Validate the execution layer:
  - `py_compile` for Python
  - browser rendering for HTML
  - JSON parse for JSON files

## Git Merge Conflicts With Mojibake-On-One-Side

A common Japanese-repo failure mode: one branch (often the older / Windows-saved branch)
was committed with CP932 / Shift-JIS bytes stored as UTF-8 garbage, while the other
branch is properly UTF-8. `git merge` then produces conflicts where one half is
unreadable mojibake.

Do NOT try to hand-merge mojibake against clean text. The cleaner branch is the
source of truth — pull it in wholesale.

Workflow:

1. For each conflicted text file (README, .bat, .md, .html), inspect both sides:
   - `git show :2:<path>` shows ours (HEAD)
   - `git show :3:<path>` shows theirs (incoming)
2. If one side is mojibake and the other is clean UTF-8:
   - Take the clean side: `git checkout --ours <path>` or `git checkout --theirs <path>`
   - Re-apply any meaningful additions from the mojibake side **manually** using
     trusted content (commit messages, PR descriptions, or earlier UTF-8 ancestors),
     not by copying mojibake bytes.
3. After resolving, run a sanity grep for mojibake fragments across the merged tree
   to confirm nothing leaked in:

```bash
grep -rEn '繧|縺|蜑|逞|﻿' --include='*.md' --include='*.bat' --include='*.tsx' --include='*.ts' .
```

4. Also check for a stray UTF-8 BOM (`﻿` / `﻿`) at the start of `.bat` files —
   Windows `cmd.exe` will print it as a stray character on the first line.

Sub-rules for `.bat` files specifically:

- Keep `chcp 65001 >nul` on line 1 (after `@echo off`).
- Do not allow a BOM before `@echo off` — strip it if present.
- If the file becomes unreadable after a merge, prefer the side that already had
  `chcp 65001` and proper UTF-8 — Windows-saved CP932 .bat files will not survive
  a UTF-8 repository round-trip.
