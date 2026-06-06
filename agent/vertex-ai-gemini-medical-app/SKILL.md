---
name: vertex-ai-gemini-medical-app
description: Build, migrate, and debug Next.js / Node.js medical apps that call Gemini via Google Vertex AI (`@google/genai` with `vertexai: true`). Covers ADC auth, current Gemini model IDs (3.5 / 3.1 / 3.0 / 2.5), region constraints (global / us / eu / asia-northeast1), Server Action patterns with image/PDF `inlineData`, and clipboard-paste UI for clinical document upload. TRIGGER when: code imports `@google/genai`; `GoogleGenAI({ vertexai: true, project, location })` appears; env vars `GOOGLE_CLOUD_PROJECT` / `GOOGLE_CLOUD_LOCATION` / `GOOGLE_APPLICATION_CREDENTIALS` are referenced; user migrates from Gemini API Key to Vertex AI; user updates Gemini model IDs; user hits `Publisher Model ... was not found`, `Could not load the default credentials`, or region/404 errors with Gemini; user builds clinical summary / 紹介状 / カルテ要約 features on Vertex. SKIP: file imports `@google/generative-ai` (legacy SDK without Vertex), `openai`, or `@anthropic-ai/sdk`; non-medical generic chat apps; pure Google AI Studio (API key only) projects with no plan to move to Vertex.
---

# Vertex AI × Gemini を医療系 Next.js アプリで運用する

このスキルは、日本の医療現場（クリニック・病院）で Vertex AI 経由の Gemini を使う Next.js / Node.js アプリを対象とする。`@google/genai` v1.42+ を前提とし、API Key 方式ではなく **Vertex AI（ADC 認証）** を正とする。

## 1. 初期化パターン（必ずこの形）

```ts
import { GoogleGenAI } from "@google/genai";

const ai = new GoogleGenAI({
  vertexai: true,
  project: process.env.GOOGLE_CLOUD_PROJECT,
  location: process.env.GOOGLE_CLOUD_LOCATION || "global",
});
```

- API Key 方式 `new GoogleGenAI({ apiKey })` とは別物。**Vertex 用途では絶対に混在させない**。
- `location` 未指定時のデフォルトは `"global"`（最新モデルが最も多く解放されている）。
- Server Action / Route Handler 内で都度生成して問題ない（軽量）。Edge Runtime では動かないため `runtime = "nodejs"` を指定する。

## 2. リージョン選定（重要）

| location | 対応モデル | 用途 |
|---|---|---|
| `global` | 3.5 Flash 含む全 GA + 主要 Preview | **デフォルト推奨** |
| `us-central1` / `us` / `eu` | 3.5 Flash 等の US/EU 限定モデル | リージョン要件あり |
| `asia-northeast1` | 3.1 Preview / 3.0 Preview / 2.5 GA | **3.5 Flash は 404**。低レイテンシ重視時のみ |

迷ったら `global`。日本ユーザー向けでも `asia-northeast1` を選ぶと最新 Flash が使えなくなる罠がある。

詳細は [references/regions.md](references/regions.md)。

## 3. 現行 Gemini モデル ID（2026-05 確認済み）

臨床用途では **3.0 以上が必須**。2.5 以下は精度不足で診療補助には使わない（接続テスト用にのみ残す）。

| モデル ID | 状態 | 用途 |
|---|---|---|
| `gemini-3.5-flash` | GA | **主力**。near-Pro 精度、Flash 価格。global/us/eu |
| `gemini-3.1-pro-preview` | Preview | 最高精度が必要なとき |
| `gemini-3.1-flash-lite-preview` | Preview | 軽量・高速 |
| `gemini-3-pro-preview` | Preview | 3.1 が不安定なときの代替 |
| `gemini-3-flash-preview` | Preview | 同上 |
| `gemini-2.5-pro` / `gemini-2.5-flash` | GA | **接続テスト・fallback 専用**。臨床本番には使わない |

モデル選択 UI を作るときは「3.5 Flash を既定」「2.5 系には『接続確認用』ラベル」を付ける。

詳細は [references/models.md](references/models.md)。

## 4. 認証（ADC）

開発機（推奨）:
```bash
gcloud auth application-default login
```

サーバ / CI:
```bash
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
```

`.env.local` には **キー JSON を置かない**。パスのみ記載し、JSON 自体は `.gitignore` 配下に置く。サービスアカウントには `roles/aiplatform.user` を付与する。

## 5. Server Action での呼び出しパターン

```ts
"use server";
import { GoogleGenAI } from "@google/genai";

export async function summarize(files: File[], prompt: string) {
  const ai = new GoogleGenAI({
    vertexai: true,
    project: process.env.GOOGLE_CLOUD_PROJECT!,
    location: process.env.GOOGLE_CLOUD_LOCATION || "global",
  });

  const contentParts: any[] = [{ text: prompt }];
  for (const f of files) {
    const buf = Buffer.from(await f.arrayBuffer());
    contentParts.push({
      inlineData: { data: buf.toString("base64"), mimeType: f.type },
    });
  }

  const response = await ai.models.generateContent({
    model: "gemini-3.5-flash",
    contents: contentParts,
  });
  return response.text || "";
}
```

- 画像 / PDF は `inlineData`（base64）で渡す。20MB 超は Files API を検討。
- `response.text` は `undefined` の場合があるので必ず `|| ""` で守る。
- 失敗時のリトライは指数バックオフ。429 / 503 のみリトライ、4xx の Publisher 404 はリトライしない（モデル ID/リージョン誤りなので即エラー表示）。

## 6. 典型エラー → 対処

| エラー | 原因 | 対処 |
|---|---|---|
| `Could not load the default credentials` | ADC 未設定 | `gcloud auth application-default login` か `GOOGLE_APPLICATION_CREDENTIALS` を設定 |
| `Publisher Model ... was not found` | モデル ID とリージョン不整合 | location を `global` に戻す、またはモデル ID を見直す。特に `asia-northeast1` × `gemini-3.5-flash` は不可 |
| `PERMISSION_DENIED: Vertex AI API has not been used` | API 未有効化 | `gcloud services enable aiplatform.googleapis.com` |
| `404 ... models/<id>:generateContent` | レガシー SDK (`@google/generative-ai`) と Vertex 混在 | `@google/genai` に統一、`vertexai: true` を確認 |
| Windows: `npm` が PowerShell でブロック | ExecutionPolicy | `cmd /c npm install` で迂回、または `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| Windows `setup.bat` で `node` 不検出 | PATH に未追加 | `setup.bat` 冒頭に `if exist "C:\Program Files\nodejs" set "PATH=%PATH%;C:\Program Files\nodejs"` |

網羅版は [references/troubleshooting.md](references/troubleshooting.md)。

## 7. 臨床ドキュメント UI: マウス単独でクリップボード貼付け

医師は片手キーボード操作が難しい場面が多い（手袋・採血直後等）。**Ctrl+V を要求しない** UI が望ましい。

```ts
async function pasteFromClipboard(): Promise<File[]> {
  const items = await navigator.clipboard.read();
  const files: File[] = [];
  for (const item of items) {
    for (const type of item.types) {
      if (type.startsWith("image/") || type === "application/pdf") {
        const blob = await item.getType(type);
        const ext = type.split("/")[1];
        files.push(new File([blob], `pasted-${Date.now()}.${ext}`, { type }));
      }
    }
  }
  return files;
}
```

制約:
- **HTTPS または localhost 必須**（Clipboard API はセキュアコンテキスト限定）
- **ユーザージェスチャ必須**（ボタン onClick から呼ぶ。自動実行不可）
- Permissions API で `clipboard-read` 状態を確認すると UX が向上

## 8. 医療データ取り扱い注意

- **PHI / 患者識別子をプロンプトに含めない**ことを既定とする（氏名は仮名化、ID は院内 ID のみ）。
- Vertex AI のデータ保持設定は GCP コンソール「Vertex AI Studio Settings」で確認。診療データを扱う場合は **データロギング無効化** をプロジェクトポリシーで明文化する。
- 個人情報設定法・医療情報システム安全管理ガイドライン（厚労省）に沿う運用を前提。

## 開発フロー（チェックリスト）

新規セットアップ時:
1. `gcloud auth application-default login`
2. `gcloud services enable aiplatform.googleapis.com`
3. `.env.local` に `GOOGLE_CLOUD_PROJECT` と（必要なら）`GOOGLE_CLOUD_LOCATION=global`
4. `npm i @google/genai`
5. `gemini-2.5-flash` で疎通テスト → 成功したら `gemini-3.5-flash` に切替

モデル更新時:
1. [references/models.md](references/models.md) で現行 ID を確認
2. リージョン互換を [references/regions.md](references/regions.md) で確認
3. UI のモデル選択肢を更新し、既定を 3.5 Flash に

## Related Skills

このスキルは **「Vertex AI 経由で Gemini を呼ぶ実装層」** の知識を扱う。
医療系の case ベースアプリ全体の設計（フォルダ構造、PHI 分離、レビュー UI、ルール層）は
別スキルに分かれている:

- `medical-case-app-patterns` — case workspace 設計、ローカル前処理と LLM 投入の分離、レビュー
  UI、JSON 出力の正規化、再利用可能な医療アプリ設計パターン。**新規アプリ設計時はまずこちらを参照**
  し、本スキルは Gemini 呼び出し実装段階で併用する。
- `text-encoding-guard` — Vertex 移行作業中に発生しがちな `setup.bat` / README の mojibake、
  特に古い API Key 版ブランチとのマージコンフリクト対処。`references/file-recovery.md` の
  「Git Merge Conflicts With Mojibake-On-One-Side」セクションを参照。
- `phi-redaction-review` — Gemini に投入する前に PHI を機械的に削るルール設計。
  本スキル §8（医療データ取り扱い注意）を実装するときに併用。
