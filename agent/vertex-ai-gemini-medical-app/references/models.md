# Gemini モデル ID 一覧（2026-05 時点）

## GA（本番利用可）

### gemini-3.5-flash  ★主力
- near-Pro 精度、Flash 価格。臨床要約・紹介状下書き・カルテ整形の既定モデル。
- 対応: `global`, `us-central1`, `us`, `eu`
- 非対応: `asia-northeast1`（404 になる）
- マルチモーダル: text / image / PDF / audio

### gemini-2.5-pro / gemini-2.5-flash
- GA だが精度は 3.x より劣る。**臨床本番では使わない**。
- 用途: ADC や Vertex API 有効化の **疎通確認専用**（全リージョンで動くので原因切り分けに便利）。
- UI に出すなら「接続確認用」ラベルを付ける。

## Preview（評価・限定運用）

### gemini-3.1-pro-preview
- 現状の最高精度。長文・複雑な臨床推論が必要なとき。
- SLA は Preview 相当。本番フォールバック先には不向き。

### gemini-3.1-flash-lite-preview
- 3.5 Flash より軽量・安価。短文要約・分類タスク向け。

### gemini-3-pro-preview / gemini-3-flash-preview
- 3.1 系が不安定なときの代替。新規採用は 3.1 系を優先。

## 選定ガイド

| ユースケース | 既定 | フォールバック |
|---|---|---|
| 臨床サマリ生成 | `gemini-3.5-flash` | `gemini-3.1-pro-preview` |
| 紹介状下書き | `gemini-3.1-pro-preview` | `gemini-3.5-flash` |
| 検査値分類・タグ付け | `gemini-3.1-flash-lite-preview` | `gemini-3.5-flash` |
| 接続テスト | `gemini-2.5-flash` | — |

## モデル一覧の確認コマンド

```bash
gcloud ai models list --region=global --project=$GOOGLE_CLOUD_PROJECT
```

または Vertex AI Studio の Model Garden で「Gemini」フィルタ。
