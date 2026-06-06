---
name: text-encoding-guard
description: Prevent, diagnose, and fix mojibake and text encoding corruption when reading or editing source files across Windows terminals, PowerShell, Python, HTML, Markdown, JSON, and agent workflows. Use when text appears garbled, Japanese characters become unreadable, a file looks correct in one tool but broken in another, or Codex needs to edit files without introducing encoding regressions.
---

# Text Encoding Guard

Assume encoding is fragile until proven otherwise.

Use this skill before editing human-readable text files when mojibake is possible or has already appeared.

## Core Workflow

1. Identify where the corruption actually lives.
   Distinguish between:
   - terminal display corruption
   - file-content corruption
   - browser rendering issues
   - mixed-encoding copy/paste damage

2. Verify the file contents with a trusted reader.
   Prefer reading the file in Python with explicit `encoding="utf-8"` when possible.
   Do not trust a PowerShell or terminal preview alone if it already looks garbled.

3. Edit with an explicit encoding strategy.
   Prefer UTF-8 for source files, Markdown, HTML, JSON, CSS, JS, and Python.
   When writing files programmatically, always pass an explicit encoding.
   Avoid accidental shell redirection workflows that inherit a hostile code page.

4. Re-verify after writing.
   Check the file content again with an explicit UTF-8 read.
   If the file is user-facing, also check the actual rendering layer such as browser output.

5. Preserve meaning before attempting rescue.
   If the file content itself is already corrupted, do not keep rewriting the mojibake.
   Reconstruct from a clean source, version control, or a trusted copy if available.

## Decision Rules

- If a file looks broken only in terminal output but UTF-8 reads correctly in Python, treat it as a display problem first.
- If both Python UTF-8 reads and browser rendering are broken, treat it as file-content corruption.
- If a web page is garbled, confirm both the file encoding and the HTML charset declaration.
- Prefer rewriting short text assets completely rather than patching around partially corrupted strings.
- Prefer ASCII-only status messages in `.bat` files when Windows code page behavior is unpredictable.

## Safe Practices

- Use `Path.read_text(encoding="utf-8")` and `Path.write_text(..., encoding="utf-8")` for text files.
- Keep `<meta charset="UTF-8">` near the top of HTML documents.
- Treat PowerShell `Get-Content` output as potentially misleading for non-ASCII text.
- Use Unicode escape sequences when you need a code-page-independent way to inject known text through a hostile terminal path.
- After fixing a file, search for common mojibake fragments before declaring success.

## What To Read Next

- Read `references/windows-terminal.md` when the terminal output is suspicious.
- Read `references/file-recovery.md` when the file bytes or saved content are already corrupted.

## Repository Sharing

- Keep this skill inside the repository when you want other terminals and agents to share it through git.
- If a team also wants auto-discovery from a user profile, copy or install the same skill into a user-level skills directory as a second step.
