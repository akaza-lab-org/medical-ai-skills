---
name: windows-clinic-aux-exe-deploy
description: Distribute a third-party executable (e.g. SumatraPDF) to clinic terminals via a shared deploy folder without bundling it in the main release zip. Use when a portable Windows clinic app needs an auxiliary exe that is too large to ship in every release, must survive release updates, and should work without manual path configuration on each terminal.
---

# windows-clinic-aux-exe-deploy

Use this skill when a portable clinic app needs an auxiliary executable (such as SumatraPDF for direct printing) that should be:

- Distributed once via the SMB shared folder rather than bundled in every release zip
- Placed in a location that survives release updates (outside the `current/` junction)
- Automatically detected by the app without requiring manual settings configuration

## Directory layout

```
{INSTALL_ROOT}/                ← e.g. C:\DATA\FONC_R8
  current/                     ← junction → releases/{version}/
    app/
      services/
        pdf_printing.py        ← Python app
    run.bat                    ← sentinel used to detect installation
  tools/
    SumatraPDF.exe             ← placed here by install bat; survives updates
  releases/
    kenshin_2026.01.01_.../    ← extracted release zips
  data/                        ← junction → persistent data folder

{shared_dir}/
  deploy/
    install_sumatra.bat        ← run once per terminal from shared folder
    install_sumatra_readme.txt ← instructions for operators
    SumatraPDF.exe             ← admin places portable exe here
    clinic_settings.json
    terminals.json
```

## Why `tools/` not `current/dist/`

`current/` is a junction that switches to a new release folder on every update. Any file placed inside `current/` disappears when the junction is repointed. `{INSTALL_ROOT}/tools/` sits outside the junction and is untouched by `update_from_share.ps1` or any release switch.

## Install bat — key design decisions

Place `install_sumatra.bat` in the shared `deploy/` folder alongside `SumatraPDF.exe`.

```bat
@echo off
chcp 65001 >nul
setlocal EnableExtensions

set "SRC=%~dp0SumatraPDF.exe"   ← %~dp0 resolves to the bat's own folder,
                                   whether that is a UNC path or a drive letter.
                                   Running directly from \\SERVER\share\ works.
set "FOUND=0"
set "COPY_FAILED=0"

if not exist "%SRC%" (
  echo [ERROR] SumatraPDF.exe が見つかりません: %SRC%
  pause & exit /b 1
)

:: Detect all installed environments by checking for the sentinel run.bat.
:: Loop over all possible INSTALL_ROOTs (production + test/staging coexist).
for %%R in ("C:\DATA\FONC_R8" "C:\DATA\FONC") do (
  if exist "%%~R\current\run.bat" (
    set "FOUND=1"
    if exist "%%~R\tools\SumatraPDF.exe" (
      echo [INFO] Already installed: %%~R\tools\SumatraPDF.exe
    ) else (
      if not exist "%%~R\tools" mkdir "%%~R\tools"
      copy /Y "%SRC%" "%%~R\tools\SumatraPDF.exe" >nul
      if errorlevel 1 (
        echo [ERROR] Copy failed for %%~R
        set "COPY_FAILED=1"
      ) else (
        echo [INFO] Installed: %%~R\tools\SumatraPDF.exe
      )
    )
  )
)

if "%COPY_FAILED%"=="1" ( pause & exit /b 1 )
if "%FOUND%"=="0" (
  echo [ERROR] No installed environment found. Run setup first.
  pause & exit /b 1
)

echo Done. App will auto-detect SumatraPDF on next startup.
pause & exit /b 0
```

### Why `FOUND` and `COPY_FAILED` are separate

If all environments are already installed, `COPY_FAILED` stays 0 and the bat exits cleanly. Only an actual copy failure triggers a non-zero exit. Combining both flags into one variable would incorrectly report "not found" when the correct state is "already installed, nothing to do".

### UNC path execution

`%~dp0` expands to the folder containing the bat, including UNC paths (`\\SERVER\share\deploy\`). Windows CMD can run bat files from UNC paths and `%~dp0` works correctly. No drive mapping required.

### Sentinel detection

Use `current\run.bat` (not just the directory) as the sentinel for a valid installation. The `current\` junction may exist as an artifact even when the install is incomplete; `run.bat` inside it confirms a real release is in place.

## Python app — auto-detect fallback chain

Resolve the exe path with a priority chain so that:
1. Explicit operator configuration is always respected.
2. A `tools/`-installed exe is used automatically without any settings change.
3. A bundled fallback (if the exe is ever shipped inside the release zip) works as a last resort.

```python
def _resolve_sumatra_exe() -> Optional[str]:
    """sumatra_exe_path setting → {install_root}/tools/ → dist/ in order."""
    from app.services.settings_service import load_settings

    settings = load_settings()
    configured = str(settings.get("sumatra_exe_path") or "").strip()
    if configured and Path(configured).exists():
        return configured

    # install_sumatra.bat places the exe 4 levels up from this file:
    # current/app/services/pdf_printing.py → current/ → {INSTALL_ROOT}/
    tools_path = Path(__file__).parent.parent.parent.parent / "tools" / "SumatraPDF.exe"
    if tools_path.exists():
        return str(tools_path)

    # Bundled inside release zip at dist/SumatraPDF.exe (legacy / CI fallback)
    bundled = Path(__file__).parent.parent.parent / "dist" / "SumatraPDF.exe"
    if bundled.exists():
        return str(bundled)

    return None
```

The `parent.parent.parent.parent` traversal assumes the file is at `{install_root}/current/app/services/<file>.py`. Adjust depth for a different module layout.

### Settings form interaction

When the operator fills in `sumatra_exe_path` explicitly in the settings UI, that value takes priority and overrides the `tools/` auto-detect. Leave `sumatra_exe_path` empty in `DEFAULT_SETTINGS` so that a terminal that has never configured the field automatically falls through to `tools/`.

## Deploy folder structure for `clinic_settings.json`

Include all shared printer fields in `clinic_settings.json` so that new terminals pick up the correct values during first-time `Apply-Settings()`:

```json
{
  "exam_ticket_printer": "EPSON PX-S890X",
  "printer_a4": "EPSON PX-S890X",
  "printer_a5": "EPSON PX-S890X"
}
```

If `printer_a4` or `printer_a5` are missing from `clinic_settings.json`, new terminals get empty strings for those keys in their local `settings.json`. Even though the shared folder's `settings.json` may have correct values that the app reads at runtime, a full-form save from the new terminal can overwrite the shared file with the empty strings (see `shared-folder-sqlite-clinic-ops` → Shared settings overwrite protection).

## Readme for operators

Include a plain-text readme in the `deploy/` folder explaining:

1. What exe to download and where to rename it
2. Run `install_<tool>.bat` from the shared folder — no drive mapping needed
3. What happens (install path, skip if already present)
4. How the app auto-detects it (no settings page required)
5. Troubleshooting (exe not found, copy failure → run as administrator)

## Generalizing to other auxiliary executables

The same pattern applies to any tool the app shells out to:

| Tool | Suggested setting key | Auto-detect path |
|---|---|---|
| SumatraPDF | `sumatra_exe_path` | `tools/SumatraPDF.exe` |
| AutoHotkey | `ahk_exe_path` | `tools/AutoHotkey64.exe` |
| Ghostscript | `gs_exe_path` | `tools/gswin64c.exe` |

Each tool gets its own `install_<tool>.bat` in `deploy/` and its own fallback path in the resolver function. Keep the priority order consistent: explicit setting → `tools/` → `dist/` → `None`.
