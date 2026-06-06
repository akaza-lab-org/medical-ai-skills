# Vertex AI × Gemini トラブルシュート

## 認証系

### `Could not load the default credentials`
ADC 未設定。
```bash
gcloud auth application-default login
```
CI など gcloud が使えない環境では:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/sa.json
```

### `PERMISSION_DENIED: Vertex AI API has not been used in project ... before or it is disabled`
```bash
gcloud services enable aiplatform.googleapis.com --project=$GOOGLE_CLOUD_PROJECT
```
反映に 1〜2 分かかることがある。

### `PERMISSION_DENIED: Permission 'aiplatform.endpoints.predict' denied`
サービスアカウントの IAM ロール不足。
```bash
gcloud projects add-iam-policy-binding $GOOGLE_CLOUD_PROJECT \
  --member=serviceAccount:<SA_EMAIL> \
  --role=roles/aiplatform.user
```

## モデル / リージョン系

### `Publisher Model projects/.../models/<id> was not found` / 404
1. モデル ID を確認（typo、preview suffix 付け忘れなど）
2. リージョンを `global` に戻して再試行
3. それでも 404 なら [references/models.md](models.md) で現行 ID を確認

特に `gemini-3.5-flash` × `asia-northeast1` は **必ず 404**。

### `INVALID_ARGUMENT: Request contains an invalid argument`
- `contents` の構造ミスが多い。`[{ text }, { inlineData: { data, mimeType } }]` の配列であること。
- `inlineData.data` は **base64 文字列**。Buffer を直接渡すと失敗。

## SDK 系

### `@google/generative-ai` と `@google/genai` の混同
- `@google/generative-ai`（旧 SDK）は Vertex AI 非対応／対応が限定的。
- 新規は **必ず `@google/genai`** を使う。`package.json` に旧 SDK が残っていたら削除。

### `response.text is not a function` / `undefined`
v1.42+ では `response.text` は **プロパティ**（関数ではない）。
```ts
const text = response.text || "";   // OK
const text = response.text();       // NG（古い API）
```

## Next.js 固有

### Edge Runtime で動かない
`@google/genai` は Node.js ランタイム必須。Route Handler / Server Action で:
```ts
export const runtime = "nodejs";
```

### Server Action のレスポンスサイズ制限
大きい PDF を base64 で送ると body size limit に当たる。`next.config.js`:
```js
experimental: { serverActions: { bodySizeLimit: "20mb" } }
```

## Windows 開発環境

### PowerShell で `npm` がブロックされる
```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```
または `cmd /c npm install` で迂回。

### `setup.bat` で `'node' is not recognized`
PATH に Node.js が無い。`setup.bat` 冒頭に追加:
```bat
if exist "C:\Program Files\nodejs" set "PATH=%PATH%;C:\Program Files\nodejs"
```

### `gcloud` コマンドが見つからない
Google Cloud SDK をインストール後、新しいターミナルを開き直す（PATH 再読込）。

## レート制限 / リトライ

- 429 / 503 のみ指数バックオフでリトライ（初回 1s、最大 3 回）。
- 4xx（特に 400 / 404）は **リトライしない**。プロンプトかモデル ID の問題なので即フェイル。
- Vertex のクォータは GCP Console「IAM & Admin > Quotas」で `aiplatform.googleapis.com` を検索して引き上げ申請。

## デバッグの最初の一手

エラー時はこの順で切り分け:
1. `gemini-2.5-flash` + `location: "global"` で疎通確認 → これで通れば認証 OK
2. 通らなければ ADC か API 有効化の問題
3. 通るならモデル ID / リージョンの組み合わせ問題
