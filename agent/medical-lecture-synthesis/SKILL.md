---
name: medical-lecture-synthesis
description: Synthesize new medical or clinical lectures by analyzing and mapping legacy assets (PDF/PPTX) and manufacturer slide sets. Use when Codex needs to: (1) Inventory past lecture files over several years, (2) Map specific slide pages to a new 30-60 min lecture outline, (3) Create clinical "hook" scenarios (e.g., doctor-patient dialogues), or (4) Generate medical-context AI imagery (e.g., Manga style) to enhance engagement.
---

# Medical Lecture Synthesis

## Core Workflow

### 1. Asset Inventory and Indexing
When starting a new project based on existing slides, first index the available assets to avoid manual searching.
- Use `scripts/extract_slide_titles.py` to recursively scan directories for `.pptx` and `.pdf` files.
- Generate a `slide_list.md` that filters by date (e.g., last 5-10 years) and file type.
- Create a high-level summary of relevant files based on the lecture theme.

### 2. Structural Mapping
Once an outline is agreed upon, map specific source slides to the new structure.
- Create a `slide_reference_list.md` or `slide_mapping.md`.
- Include the exact filename and page/slide number for each section.
- Identify "gaps" where no existing material exists (e.g., specific recent trial data or localized clinical cases).

### 3. Narrative "Hooks" and Empathy Design
For physician audiences, standard clinical data can be dry. Use narrative scenarios to increase engagement.
- Design a "Doctor-Patient Dialogue" at the start of the lecture to illustrate common clinical challenges (e.g., Weight Bias, Metabolic Adaptation).
- Use `generate_image` to create visual anchors for these dialogues.
- **Manga/Webtoon Style**: Often more effective for clinical "scenarios" as it conveys emotion and empathy better than generic stock photos or dry icons.

### 4. Technical Integration
- For `.pptx` files, use `python-pptx` to extract titles and check slide layouts.
- For `.pdf` files, use `pdfplumber` to extract headers and verify content.
- When reusing manufacturer slides (e.g., Wegovy, Mounjaro), ensure citations are preserved and align them with the latest domestic guidelines (e.g., 肥満症診療ガイドライン2022).

### 5. python-pptx Template-Based Slide Generation

When generating a full draft deck from an outline using a `.pptx` template:

**Step 1 — Inspect layouts and placeholder indices before coding:**
```python
prs = Presentation(TEMPLATE)
for i, layout in enumerate(prs.slide_layouts):
    print(f'Layout[{i}]: {layout.name}')
    for ph in layout.placeholders:
        print(f'  idx={ph.placeholder_format.idx}  name={ph.name}')
```
Standard index map (confirm per template): `idx=0` = title, `idx=1` = body/subtitle/text, `idx=2` = second content column.

**Step 2 — Remove template sample slides before adding new slides:**
```python
for _ in range(len(prs.slides)):
    rId = prs.slides._sldIdLst[0].attrib.get(
        '{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
    )
    del prs.slides._sldIdLst[0]
    try:
        prs.part.drop_rel(rId)
    except Exception:
        pass
```

**Step 3 — Apply auto-fit to all title placeholders to prevent wrapping:**
```python
from pptx.enum.text import MSO_AUTO_SIZE

def set_title(slide, text):
    for p in slide.placeholders:
        if p.placeholder_format.idx == 0:
            p.text = text
            p.text_frame.auto_size = MSO_AUTO_SIZE.TEXT_TO_FIT_SHAPE
            return
```

**Step 4 — Bullet body with level-aware font sizing:**
```python
def set_body(slide, items, ph_idx=1, base_size=20):
    ph = next((p for p in slide.placeholders if p.placeholder_format.idx == ph_idx), None)
    if not ph:
        return
    tf = ph.text_frame
    tf.clear(); tf.word_wrap = True
    first = True
    for item in items:
        text, level = (item[0], item[1]) if isinstance(item, tuple) else (item, 0)
        para = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        para.level = level
        run = para.add_run()
        run.text = text
        run.font.size = Pt(base_size - level * 2)   # deeper levels slightly smaller
```

**Japanese path in docstrings**: use `\\` (e.g., `C:\\data\\`) to avoid `SyntaxWarning: invalid escape sequence`.

### 6. Figure Insertion Guide Pattern

After generating a draft deck, create `figure_insertion_guide.md` that maps every content slide to its source asset. This prevents manual searching during deck assembly.

**Required columns per row:**
- Slide # and title
- Source file (relative path from asset root)
- Referenced page/slide number and content description
- Priority: ★★★ (essential) / ★★ (recommended) / ★ (optional)
- Insertion method: **そのまま** (paste as-is) / **参考** (redraw from reference) / **新規作成** (create from scratch)

**Also include at the end:**
1. A "新規作成が必要な図表" table for gaps with no existing asset.
2. A "要確認ファイル" table for assets referenced by name but not yet located on disk (search keyword + estimated folder).

### 7. Diabetes/Obesity Slide Asset Taxonomy (Novo Nordisk / Wegovy)

Key manufacturer slide sets and their content for GLP-1 / obesity lectures:

| Asset identifier | Content | Location hint |
|-----------------|---------|---------------|
| AID9568 (JP25OB00198v2) | 肥満症総論・11の健康障害・3%減量の意義・代謝適応 | `赤座至先生_ウゴービスライドセット` |
| AID9643 / JP26SEMO00080 | SELECT試験・ウゴービブランドストーリー | 同上 |
| JP24SEMO00184 | 代謝適応とGLP-1受容体作動薬の機序 | 同フォルダまたは `治療` |
| JP24SEMO00126 | 肥満症診療ガイドライン2022スライド | 同フォルダまたは `治療` |
| JP25CO00010 (ActionIO) | 医師・患者の意識乖離データ | 同フォルダ（要検索） |
| ノボ資料/2021/GLP-1概論 | インクレチン機序・学会GL概要・循環器疾患と糖尿病 | `スライド集\ノボ資料\2021` |
| ノボ資料/2021/オゼンピック | SUSTAINシリーズ・コアストーリー | 同上 |
| ノボ資料/2021/リベルサス | PIONEERシリーズ・服用スライド・MoA | 同上 |
| ノボ資料/2021/ゾルトファイ | DUALシリーズ・Overview | 同上 |

**Note**: AID9568/AID9643 files are dated 2026 — they fall outside a "past 5 years" PowerShell date filter (`-lt "2026-01-01"`). Always scan without the upper date bound, or add a separate 付録 section for recent assets.

## Reusable Resources

- **`scripts/extract_slide_titles.py`**: Extracts titles and page numbers from a list of PPTX/PDF files.
- **`lecture_outline_template.md`**: Standard structure for a 30-minute specialist-to-GP lecture.
- **`figure_insertion_guide.md`**: Per-slide asset mapping with priority and insertion method.

## Asset Inventory — PowerShell Command

Scan a Google Drive–synced folder for PPTX/PDF files in a date range:
```powershell
Get-ChildItem -Path "G:\マイドライブ\糖尿病講義スライド" -Recurse `
  -Include "*.pptx","*.pdf","*.ppt" |
  Where-Object { $_.LastWriteTime -ge "2021-01-01" -and $_.LastWriteTime -lt "2026-01-01" } |
  Select-Object FullName, Name, LastWriteTime |
  Sort-Object FullName |
  Out-String -Width 300
```
Output is large; pipe to a file or use `Format-Table -AutoSize` for inspection.

## Clinical Safety and Compliance
- Always cross-reference drug data with official package inserts (添付文書).
- Ensure patient privacy by verifying that reused case slides contain no identifiable PHI.
- Distinguish clearly between approved indications (e.g., Diabetes vs. Obesity).
