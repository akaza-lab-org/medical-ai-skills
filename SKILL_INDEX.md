# Skill Index

Complete catalog of all reusable skills available in the `agent/` directory.

## Core Skills (Shared Utilities)

- `cross-platform-paths` — Handle file paths correctly across Windows, Linux, and macOS
- `text-encoding-guard` — Detect and manage text encoding issues safely
- `settings-precedence` — Understand and manage configuration precedence rules
- `python-manager-discovery` — Discover and interact with Python environments
- `python-cli-config-menu` — Hybrid CLI/GUI config menu pattern for portable Python tools

## PDF & Document Processing

- `pdf` — Basic PDF file handling and manipulation
- `medical-pdf-preprocess` — Preprocess medical PDFs for analysis
- `pdf-digitizer-dashboard-debug` — Debug PDF digitizer dashboard issues
- `pdf-digitizer-phase1-tuning` — Phase 1 tuning for PDF digitization
- `pdf-digitizer-phase2-tuning` — Phase 2 tuning for PDF digitization
- `pdf-digitizer-phase3-case-draft` — Phase 3 case drafting for PDF digitization
- `pdf-digitizer-project-ops` — Project operations for PDF digitization

## OCR & Form Processing

- `ocr-review-reconciliation` — Design workflows where OCR output seeds forms and humans reconcile values
- `pdf-form-coordinate-tuning` — Debug and tune PDF form field coordinate rendering and exports
- `form-roundtrip-verification` — Verify end-to-end form data integrity through import, edit, save, and reload cycles

## LLM & AI Platform

- `vertex-ai-gemini-medical-app` — Build/migrate/debug Next.js or Node.js medical apps that call Gemini via Google Vertex AI (`@google/genai` with `vertexai: true`). Covers ADC auth, current model IDs (3.5/3.1/3.0/2.5), region constraints (global/us/eu vs asia-northeast1), Server Action `inlineData` patterns, clipboard-paste UI

## Medical Applications

- `medical-case-app-patterns` — Design patterns for medical case applications
- `case-review-refresh` — Refresh and manage case reviews
- `case-workspace-operator` — Operate medical case workspaces
- `phi-redaction-review` — Review and manage PHI redaction rules
- `medical-ahk-emr-bridge` — Bridge a local medical app to an AHK automation stack and EMR screens
- `shared-folder-sqlite-clinic-ops` — Multi-terminal clinic app with SMB SQLite, role guards, health checks, backups, conflict checks, editor locks, rollout rehearsal, and shared settings overwrite protection
- `windows-clinic-aux-exe-deploy` — Distribute a third-party exe (e.g. SumatraPDF) to clinic terminals via shared deploy folder; install bat with UNC-safe %~dp0, multi-INSTALL_ROOT detection, app-side auto-detect fallback chain
- `windows-registered-label-printing` — Queue-based label printing via Windows-registered LAN printers across terminals

## Clinical Lecture & Presentation

- `clinical-lecture-ppt-refinement` — Refine medical PPTX lectures for projection: standard 16:9 layout, blue header + red emphasis palette, python-pptx/lxml helpers, placeholder pitfalls, COM-based preview
- `medical-lecture-synthesis` — Map past PPT/PDF lecture assets into a new lecture outline (upstream of refinement)
- `clinical-pdf-overlay-forms` — Build coordinate-driven PDF overlays on non-fillable medical forms

## Testing & Quality Assurance

- `debug-failing-test` — Debug and troubleshoot failing tests
- `regression-checker` — Detect and analyze regressions
- `run-e2e-tests` — Execute end-to-end tests
- `run-integration-tests` — Execute integration tests
- `run-smoke-tests` — Execute smoke tests
- `run-pre-commit-checks` — Run pre-commit validation checks

## Automation & Browser Testing

- `ahk-legacy-automation` — AutoHotkey GUI automation for legacy systems, EMR, and Word VBA integration
- `playwright` — Browser automation with Playwright
- `playwright-react-readonly-bypass` — Workaround for automating React/Vue readonly custom inputs
- `playwright-interactive` — Interactive Playwright debugging and testing
- `screenshot` — Capture and manage screenshots
- `spreadsheet` — Manipulate spreadsheets programmatically
- `tobu-ticket-downloader` — Download and manage TOBU tickets

## Development & Code Generation

- `java-lsp-tools` — Language Server Protocol tools for Java
- `frontend-skill` — Frontend development patterns and utilities
- `generate-snapshot` — Generate and manage test snapshots
- `schema-field-sync` — Keep field definitions aligned across database, API, forms, OCR prompts, templates, and exports
- `skill-creator` — Create new skills programmatically
- `skill-collector` — Collect and organize skills
- `skill-installer` — Install and manage skills

## System Skills (.system folder)

Advanced and specialized skills for system-level operations:

- `.system/imagegen` — Image generation using AI models
- `.system/openai-docs` — OpenAI documentation and API reference
- `.system/plugin-creator` — Create AI plugins and extensions
- `.system/skill-creator` — Advanced skill creation with automation
- `.system/skill-installer` — Advanced skill installation and management

---

## Usage

To use a skill:

1. **Locate the skill** in the appropriate category above
2. **Read its `SKILL.md`** file to understand purpose, instructions, and examples
3. **Follow the skill's instructions** for implementation or usage
4. **Register new skills** by adding them to this index

### For AI Agents (Claude, Cursor, Cline, etc.)

When you have a task:
1. Scan this index for relevant skills
2. Read the skill's `SKILL.md` to understand its capabilities
3. Use the skill's instructions to guide your implementation
4. Update or improve skills as needed

---

## Auto-Discovery

Skills are automatically available at:
- **Claude Code**: `~/.claude-code/agents/` (junction to this repository)
- **Codex**: `~/.codex/skills/` (junction to this repository)
- **Antigravity**: `~/.gemini/antigravity/skills/` (junction to this repository)
- **Cline/Roo Code**: `.clinerules` configuration in project root

Run the setup script to enable auto-discovery:
```powershell
.\setup-shared-skills.ps1
# or
.\automation\setup_env.ps1
```
