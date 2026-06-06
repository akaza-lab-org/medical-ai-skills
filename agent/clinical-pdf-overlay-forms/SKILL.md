---
name: clinical-pdf-overlay-forms
description: Build, revise, and maintain fixed-layout medical or administrative PDF overlays that print application data onto non-fillable forms. Use when Codex needs to place text, marks, page numbers, or QR codes onto a blank template PDF, compare generated output to a sample form, keep yearly layout changes maintainable, or combine coordinate JSON with `pdf_digitizer` and related tuning workflows.
---

# Clinical PDF Overlay Forms

Use this skill for non-fillable paper forms that the app must print onto with stable coordinates.

Prefer a maintainable overlay workflow over one-off coordinate hacking. The goal is to survive yearly form changes with minimal rework.

## Inputs To Gather

Collect these before editing code:

- blank template PDF
- one filled example, scan, or screenshot if available
- representative real data
- current coordinate source, if one already exists

If the request lacks a blank template and a visual reference, say that confidence will be lower.

## Workflow

1. Decide whether overlay is the right strategy.
   Overlay is a good fit when the form is fixed-layout, mostly repeats year to year, and only some columns are app-generated. If the form is truly dynamic or fully digital, prefer another rendering path.

2. Separate what is fixed from what is variable.
   Identify:
   - fixed header blocks
   - repeating row blocks
   - empty regions intentionally left for handwriting
   - future machine-readable metadata such as page number or QR

3. Model layout by anchors, not isolated coordinates.
   Prefer:
   - column anchors plus row offsets for tabular forms
   - named semantic blocks for headers and footers
   - one canonical coordinate source
   Avoid storing every cell as an unrelated hard-coded point unless the form truly requires it.

4. Keep template and coordinates versioned separately.
   Split:
   - yearly template PDF
   - yearly coordinate JSON or equivalent
   - rendering code shared across years when possible

5. Render the smallest useful slice first.
   Start with one row or one semantic block. Verify on an actual PDF before expanding to the full page or pagination logic.

6. Add machine-readable recovery hooks early.
   If the form may later be scanned or partially re-imported, embed stable metadata such as:
   - page number
   - total pages
   - document tag
   - QR code payload

7. Verify visually, not only numerically.
   Render the output PDF and compare it with the blank template and filled sample. A coordinate fix is not done until the page looks right.

## Coordinate Strategy

- Prefer `column anchor + row height + row index` for lists and registries.
- Keep field IDs stable across UI, DB mapping, JSON, and PDF renderer.
- Treat page assignment and coordinate origin as first-class rules.
- If a mark glyph renders unreliably, draw it as lines or shapes instead of trusting the font.
- When multiple coordinate sources exist, make precedence explicit and avoid silent replacement.

## Grid Text Writer（マス目・1文字ずつ配置）

BML依頼伝票や保険証番号欄など、1文字ごとに固定マスが印刷されているフィールドには通常の `drawString` は使えない。

```python
def draw_grid_text(c, text, start_x, y, step, font_name, font_size):
    c.setFont(font_name, font_size)
    for i, ch in enumerate(text):
        c.drawString(start_x + i * step, y, ch)
```

`layout.json` でのグリッドフィールド定義：

```json
{
  "patient_kana": {
    "x": 120, "y": 630,
    "grid_step": 12,
    "max_chars": 10
  }
}
```

実装ルール：

- `grid_step` はフォントサイズより少し大きく取る（例: 8pt フォントなら step=10〜12）。
- 文字数が `max_chars` を超える場合は截断するか警告する（はみ出しは印刷後に気づきにくい）。
- マス目フィールドの座標は「最初のマスの左端」を基準にする。

## Japanese Font

Windows 環境での PDF 印刷には埋め込み TTF を使う。

```python
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont("IPAGothic", "ipaexg.ttf"))
```

- `HeiseiKakuGo-W5`（ReportLab 内蔵 CIDフォント）は Windows プリンタドライバとの相性で文字化けするケースがある。
- `ipaexg.ttf` / `ipaexm.ttf` を `app/fonts/` に同梱して相対パスで読む方が可搬性が高い。
- ラベル印刷など既にフォントが決まっている場合はそちらに統一する。

## Change Handling

Use this triage:

- small change
  - text label moved slightly, row height changed, one column widened
  - adjust anchors or offsets only
- medium change
  - columns added or removed, a section deleted, header rearranged
  - regenerate the initial field map, then retune
- large change
  - table structure or page logic changed materially
  - treat it like a new template, not a patch

## Working With `pdf_digitizer`

Use `pdf_digitizer` when the layout changed enough that hand-tuning is wasteful.

- Use Phase 1 to recover initial fields or regions from the new template.
- Use Phase 2 to fine-tune coordinates after the structure is roughly correct.
- Use `pdf-form-coordinate-tuning` when preview, export, and stored coordinates disagree.
- Treat generated `data_key: null`, `skip_reason`, and suspicious duplicate fields as review markers, not final truth. Either wire them deliberately or keep the reason visible for a follow-up issue.
- For multi-page copy forms, name page roles in the coordinate file before tuning. Example: `page1=city_submission`, `page2=clinic_copy`, `page3=patient_notice`. Avoid saying only "p1/p2 are same" after the form has diverging sections.
- When a later page shares only a header or upper block with an earlier page, record that scope in `coordinate_source` such as `page1_same_form`, `page1_shared_header`, or `page3_same_layout_verified_on_page2_template`.

Do not promise fully automatic yearly migration. The safer pattern is semi-automatic recovery plus human review.

**現状の注意（2026-04-29 時点）**: `pdf_digitizer` は XY スケールのずれが目立ち、完成度が高くない。新規帳票への適用時は「Phase1 で大まかな座標を取得し、必ず目視オーバーレイで確認・手動補正」を前提にすること。自動出力をそのまま信頼しない。

スケールずれが大きい場合の代替手順：

1. blank template PDF を PNG にラスタライズ（`pymupdf` / Poppler）
2. 画像ビューア上でターゲット座標をピクセルで読む
3. `(px / dpi * 72)` で pt 変換して layout.json に手打ち
4. 生成PDFの PNG と元画像を重ねて目視確認

この手順は pdf_digitizer が整備されるまでの確実な代替として有効。

## Overlay Implementation Checklist

Use this checklist after importing a coordinate JSON into the app:

- Confirm every non-null `data_key` has a value produced by the renderer's value map. A PDF that "generates" can still silently leave whole sections blank.
- Search for known field groups by prefix (`lung_diagnosis_`, `colon_test_day1_`, etc.) and verify every expected option has a bool value, including false values.
- Add small direct tests for the value map when wiring many mark fields. Direct tests catch missing keys faster than visual PDF checks.
- Generate real sample PDFs for at least: normal data, long text, every judgment/result option, intentionally empty values, and not-applicable cases.
- Render page PNGs with stable names under `tmp/<issue-or-form>_variants/` so reviewers can compare output without rerunning code.
- Keep local raw templates, scans, and OCR artifacts out of commits unless the project has an explicit safe location for them.

## Validation Checklist

- generate a real PDF, not only a preview
- check page count and page numbering
- check long names or long text edge cases
- check repeated rows near the last printable line
- check all option-mark groups, especially results/history rows where values are generated from DB enums
- check QR payload contents if used
- compare PNG renders against the source form when layout matters
- add a regression test when changing pagination, coordinate transforms, or field mapping

## Guardrails

- Do not lock business identifiers into the PDF layout before the ID rules are settled.
- Do not fill columns that operations intentionally complete by hand later.
- Do not rely on a text glyph for circles, checks, or symbols if print fidelity matters.
- Do not treat raw coordinates as truth when the rendered page disagrees.
- Do not merge yearly template changes into old coordinates blindly; reclassify the change size first.
