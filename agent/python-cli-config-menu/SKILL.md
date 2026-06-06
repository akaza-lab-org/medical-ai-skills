---
name: python-cli-config-menu
description: A hybrid CLI/GUI configuration menu pattern for portable Python tools. Use when building automation scripts that run on end-user Windows terminals where third-party GUI libraries cannot be installed, but a user-friendly interactive configuration menu with state saving (runtime_config.json) and Tkinter fallbacks for alerts is needed.
---

# Python CLI Config Menu Pattern

## Overview

When building automation scripts for non-engineer end-users (e.g., electronic medical record terminals, restricted Windows PCs), you often cannot rely on complex GUI libraries (like PyQt or Vue/Electron) due to strict environment constraints. 
This skill provides a pattern for a robust standard-library-only interactive menu.

## Core Features

1. **Text-based UI (TUI) Loop**: Uses a standard `print` and `input` loop to toggle boolean settings, pick dates, and trigger actions.
2. **State Persistence**: Loads and saves settings to `runtime_config.json` without requiring the `json` module to fail if missing.
3. **Tkinter Fallbacks**: Uses Python's built-in `tkinter.messagebox` to show native Windows confirmation prompts and completion dialogue boxes, falling back cleanly to CLI `input()` if X11/GUI is unavailable.

## Implementation Template

```python
import json
import os
import sys
from pathlib import Path

RUNTIME_CONFIG_PATH = Path("runtime_config.json")
DEFAULT_CONFIG = {
    "feature_a_enabled": True,
    "feature_b_enabled": False,
    "target_date": "2026-04-10"
}

def load_config() -> dict:
    conf = dict(DEFAULT_CONFIG)
    if RUNTIME_CONFIG_PATH.exists():
        try:
            loaded = json.loads(RUNTIME_CONFIG_PATH.read_text(encoding="utf-8"))
            conf.update({k: loaded[k] for k in DEFAULT_CONFIG.keys() if k in loaded})
        except Exception as e:
            print(f"[WARNING] Config load failed: {e}")
    return conf

def save_config(conf: dict) -> None:
    RUNTIME_CONFIG_PATH.write_text(
        json.dumps(conf, ensure_ascii=False, indent=2), encoding="utf-8"
    )

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Tkinter native confirmation dialog with CLI fallback."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        result = messagebox.askyesno("Confirm", prompt, parent=root)
        root.destroy()
        return bool(result)
    except Exception:
        suffix = "[Y/n]" if default else "[y/N]"
        answer = input(f"{prompt} {suffix}: ").strip().lower()
        if not answer:
            return default
        return answer in ("y", "yes", "1")

def show_completion_popup(message: str) -> None:
    """Tkinter native info dialog with CLI fallback."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        messagebox.showinfo("Complete", message)
        root.destroy()
    except Exception:
        print(f"[INFO] {message}")

def configure_menu(conf: dict) -> tuple[dict, str]:
    working = dict(conf)
    while True:
        print("\n====================================")
        print(" Settings Menu")
        print("====================================")
        print(f"1. Feature A    : {'ON' if working['feature_a_enabled'] else 'OFF'}")
        print(f"2. Feature B    : {'ON' if working['feature_b_enabled'] else 'OFF'}")
        print(f"3. Target Date  : {working['target_date']}")
        print("8. Save & Run")
        print("9. Cancel")
        
        choice = input("Select [1-3, 8-9]: ").strip()
        
        if choice == "1":
            working["feature_a_enabled"] = not working["feature_a_enabled"]
        elif choice == "2":
            working["feature_b_enabled"] = not working["feature_b_enabled"]
        elif choice == "3":
            val = input("Enter new date (YYYY-MM-DD): ").strip()
            if val: working["target_date"] = val
        elif choice == "8":
            save_config(working)
            return working, "run"
        elif choice == "9":
            return conf, "cancel"
        else:
            print("[WARNING] Invalid choice.")

def main():
    conf = load_config()
    conf, action = configure_menu(conf)
    if action == "cancel":
        return
    
    print("[STEP] Running automation...")
    # ... actual heavy work here ...
    
    show_completion_popup("Task completed!")

if __name__ == "__main__":
    main()
```
