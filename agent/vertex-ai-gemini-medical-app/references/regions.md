# Vertex AI リージョン × Gemini モデル 互換マトリクス

## クイック結論

- **迷ったら `global`**。最新モデルが最も解放されている。
- `asia-northeast1` を選ぶと **3.5 Flash が 404**。日本リージョン要件がない限り推奨しない。

## マトリクス（2026-05 確認）

| モデル | global | us-central1 / us | eu | asia-northeast1 |
|---|:---:|:---:|:---:|:---:|
| gemini-3.5-flash | OK | OK | OK | **NG（404）** |
| gemini-3.1-pro-preview | OK | OK | OK | OK |
| gemini-3.1-flash-lite-preview | OK | OK | OK | OK |
| gemini-3-pro-preview | OK | OK | OK | OK |
| gemini-3-flash-preview | OK | OK | OK | OK |
| gemini-2.5-pro | OK | OK | OK | OK |
| gemini-2.5-flash | OK | OK | OK | OK |

## location 値の意味

- `global` … マルチリージョン。Google が最適なリージョンにルーティング。レイテンシは最良ではないが可用性最高。
- `us-central1` / `europe-west4` 等 … 単一リージョン。データレジデンシー要件がある場合に使う。
- `us` / `eu` … 大陸単位のマルチリージョン。
- `asia-northeast1` … 東京。日本国内データレジデンシー要件がある場合のみ。

## データレジデンシーが必要なクリニックの判断

医療情報を **国内処理** したい要件がある場合:
1. `asia-northeast1` を選ぶ
2. モデルは `gemini-3.1-pro-preview` か `gemini-2.5-pro` を主力にする
3. UI には「3.5 Flash は本構成で使用不可」と明記

要件がなければ `global` + `gemini-3.5-flash` が最も実用的。
