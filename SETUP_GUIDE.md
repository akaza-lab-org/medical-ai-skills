# Setup Guide: Shared Skills for AI Agents

This guide shows how to set up shared skills for **Claude Code**, **Codex**, **Antigravity**, **Cline**, **Cursor**, and **Roo Code** on any Windows machine.

## Quick Start (Recommended)

### Option 1: Automatic Setup (PowerShell)

1. **Clone or navigate to the skills repository:**
   ```powershell
   cd c:\DATA\github\skills
   ```

2. **Run the setup script:**
   ```powershell
   .\setup-shared-skills.ps1
   ```

   This creates automatic junctions for:
   - ✅ Claude Code: `~/.claude-code/agents/`
   - ✅ Codex: `~/.codex/skills/`
   - ✅ Antigravity: `~/.gemini/antigravity/skills/`

3. **Verify installation:**
   - Claude Code, Codex, and Antigravity will automatically recognize skills on next startup
   - Cline/Roo Code and Cursor will use `.clinerules` and `.cursorrules` from the project root

---

## Detailed Setup by Tool

### Claude Code (Recommended Integration)

**After running the setup script:**

1. Confirm `~/.claude-code/agents/` exists (should be a junction):
   ```powershell
   dir $env:USERPROFILE\.claude-code\agents
   ```

2. Restart Claude Code IDE or web app

3. Claude will automatically discover and use skills from the `agent/` folder

**Manual Setup** (if setup script fails):
```powershell
# Create the junction manually
cmd /c "mklink /J %USERPROFILE%\.claude-code\agents c:\DATA\github\skills\agent"
```

---

### Codex

**After running the setup script:**

1. Verify `~/.codex/skills/` exists:
   ```powershell
   dir $env:USERPROFILE\.codex\skills
   ```

2. Restart Codex

3. Access skills at: `~/.codex/skills/[skill-name]/SKILL.md`

---

### Antigravity

**After running the setup script:**

1. Verify `~/.gemini/antigravity/skills/` exists:
   ```powershell
   dir $env:USERPROFILE\.gemini\antigravity\skills
   ```

2. Restart Antigravity

3. Skills are automatically available in Antigravity

---

### Cline / Roo Code

**No additional setup required** — just ensure `.clinerules` is in your project root.

When working with this repository:
1. Cline reads `.clinerules` automatically
2. Cline scans `agent/` for `SKILL.md` files
3. Skills are immediately available

---

### Cursor

**No additional setup required** — just ensure `.cursorrules` is in your project root.

When working with this repository:
1. Cursor reads `.cursorrules` automatically
2. Cursor scans `agent/` for `SKILL.md` files
3. Skills are immediately available

---

## For Other Projects

To use these shared skills in another project:

### Method 1: Junctions (Recommended)

1. Create junctions in your project:
   ```powershell
   # Windows
   cmd /c "mklink /J .agents c:\DATA\github\skills\agent"
   ```

2. Add `.clinerules` to project root:
   ```
   This project uses shared skills from .agents/
   Use the skills in .agents/[skill-name]/SKILL.md
   ```

### Method 2: Copy Files

1. Copy the `agent/` folder to your project
2. Place `.clinerules` and `.cursorrules` in your project root
3. Update the path references in the rules files

### Method 3: Git Submodule

1. Add this repository as a submodule:
   ```bash
   git submodule add https://github.com/your-repo/skills .agents
   ```

2. Add `.clinerules` and `.cursorrules` to project root

---

## Verifying Setup

### Check Claude Code Integration

1. Open Claude Code in your IDE or web app
2. Navigate to this repository
3. Ask Claude to list available skills:
   ```
   "List all available skills in this repository"
   ```

Claude should be able to access and describe skills from `SKILL_INDEX.md`

### Check Codex Integration

```powershell
dir $env:USERPROFILE\.codex\skills
```

Should show skill folders like `pdf`, `skill-creator`, etc.

### Check Antigravity Integration

```powershell
dir $env:USERPROFILE\.gemini\antigravity\skills
```

Should show skill folders like `pdf`, `skill-creator`, etc.

### Check Cline/Roo Code

When working in a project with `.clinerules`:
1. Open Cline/Roo Code
2. Ask it to "list available skills"
3. It should scan `.agents/` or `agent/` folder

---

## Troubleshooting

### Issue: "Permission Denied" when running setup script

**Solution:** Run PowerShell as Administrator or use:
```powershell
powershell -ExecutionPolicy Bypass -NoProfile -Command ".\setup-shared-skills.ps1"
```

### Issue: Junctions not created

**Solution:** Manually create with admin privileges:
```powershell
# Run as Administrator
cmd /c "mklink /J %USERPROFILE%\.claude-code\agents c:\DATA\github\skills\agent"
```

### Issue: AI agent not finding skills

**Solution:**
1. Verify `SKILL_INDEX.md` exists in repository root
2. Verify skill folders have `SKILL.md` files
3. Restart the AI agent application
4. Check that paths use forward slashes (`/`) not backslashes (`\`)

### Issue: "Junction already exists"

**Solution:** The setup script detected an existing junction and verified it points correctly. No action needed.

If the junction points to the wrong location:
```powershell
# Remove the old junction
Remove-Item -LiteralPath $env:USERPROFILE\.claude-code\agents -Force

# Rerun setup
.\setup-shared-skills.ps1
```

---

## Maintenance

### Update Skills

Skills are updated automatically across all connected tools when you modify files in `agent/[skill-name]/`.

No restart required for most tools.

### Add New Skills

1. Create a new folder in `agent/[new-skill-name]/`
2. Add `SKILL.md` with purpose, instructions, and examples
3. Register the skill in `SKILL_INDEX.md`
4. All tools will automatically discover it on next check

### Remove Skills

1. Delete the `agent/[skill-name]/` folder
2. Remove the entry from `SKILL_INDEX.md`
3. No restart required

---

## Next Steps

- **View all available skills:** See `SKILL_INDEX.md`
- **Create a new skill:** Follow `SKILL_MANAGEMENT_GUIDE.md`
- **Project rules:** See `PROJECT_RULES.md`

For questions or issues, check the skill's `SKILL.md` file or create an issue in this repository.
