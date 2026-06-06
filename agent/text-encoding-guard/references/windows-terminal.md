# Windows Terminal and PowerShell Notes

Use this reference when text looks corrupted in terminal output.

## Common Failure Modes

- PowerShell displays mojibake even though the file is actually UTF-8
- Batch files echo non-ASCII text through a code page that does not match the file
- Copying terminal output back into a source file re-saves already corrupted text

## Safer Inspection Pattern

Prefer one of these over trusting raw terminal preview:

```powershell
@'
from pathlib import Path
print(Path(r'path\\to\\file').read_text(encoding='utf-8'))
'@ | python -
```

Or check for exact phrases:

```powershell
@'
from pathlib import Path
text = Path(r'path\\to\\file').read_text(encoding='utf-8')
print('expected phrase' in text)
'@ | python -
```

## Safer Writing Pattern

```powershell
@'
from pathlib import Path
Path(r'path\\to\\file').write_text('content here', encoding='utf-8')
'@ | python -
```

## Batch File Advice

- Prefer ASCII-only messages in `.bat` files
- Keep logic simple
- Avoid using batch output as proof that a UTF-8 file is correct

## Browser-Facing Files

For HTML, also verify:
- the file is UTF-8
- `<meta charset="UTF-8">` is present
- the browser is not showing a cached broken version
