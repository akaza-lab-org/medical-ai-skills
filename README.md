# Shared Skills Library

> **⚠️ Public mirror — read only.**
> This is a sanitized reference copy. Development and Issues are tracked in the private repository.
> Do not use this repo as a working directory for AI agents.

複数の開発環境やAIエージェントで共通利用するスキル集です。Windows では `C:\data\GitHub\skills` に統一して配置し、Codex と Antigravity の両方をこのリポジトリの `agent` へジャンクション接続する運用を標準にします。

## 新しいPCでのセットアップ

### 最短手順

新しいPCでは、まずこの 3 行だけ実行すれば使い始められます。

```powershell
git clone https://github.com/human-cto/skills C:\data\GitHub\skills
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\setup-shared-skills.ps1
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\automation\create_shortcut.ps1
```

これで:

- Codex と Antigravity の両方が同じ共有スキルを参照
- Windows ログイン時にスキル更新を自動実行

`.bat` でまとめて実行したい場合は、clone 後にこれでも同じです。

```bat
C:\data\GitHub\skills\setup-shared-skills.bat
```

### 1. リポジトリを決まった場所へ clone

```powershell
git clone https://github.com/human-cto/skills C:\data\GitHub\skills
```

`C:\data` がなければ先に作成してください。

### 2. 共通スキルリンクを作成

PowerShell で次を実行します。

```powershell
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\setup-shared-skills.ps1
```

このスクリプトが行う内容:

- `%USERPROFILE%\.codex\skills` が通常フォルダなら自動でバックアップ退避
- `%USERPROFILE%\.gemini\antigravity\skills` も同じ `agent` に接続
- `%USERPROFILE%\.codex\skills` を `C:\data\GitHub\skills\agent` へのジャンクションとして作成
- `skill-installer` と `tobu-ticket-downloader` が見えるか確認

### 3. Codex を開き直して確認

Codex で次のように依頼すると確認しやすいです。

- `有効なスキルの一覧を表示して`
- `skill-installer は使えますか？`

セッションが古い場合は、Codex を開き直すと確実です。

## 既存端末を新方式へ移行

すでに古い自動起動や旧リンク設定が入っている端末でも、次の 3 手順で移行できます。

### 1. リポジトリを標準パスへそろえる

このリポジトリが `C:\data\GitHub\skills` にあることを確認します。別パスにある場合は、この場所へ移しておくと今後の運用が簡単です。

### 2. 共通リンクを再設定

```powershell
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\setup-shared-skills.ps1
```

既存の通常フォルダは自動でバックアップされ、既存の古いジャンクションがあれば新しい共通ターゲットへ張り直されます。

### 3. 自動更新ショートカットを再作成

```powershell
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\automation\create_shortcut.ps1
```

これでスタートアップの `SyncSkills.lnk` が新方式へ更新され、ログイン時に `update-shared-skills.ps1` が実行されるようになります。

## 補足

- 管理者権限は不要です。`mklink /J` を使っています。
- スキルを更新したいときは次を実行すれば `git pull` とリンク再確認をまとめて行えます。

```powershell
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\update-shared-skills.ps1
```

- Windows 起動時に自動更新したいときは次を1回だけ実行します。

```powershell
powershell -ExecutionPolicy Bypass -File C:\data\GitHub\skills\automation\create_shortcut.ps1
```

- これでスタートアップに `SyncSkills.lnk` が登録され、ログイン時に `update-shared-skills.ps1` が自動実行されます。

- `setup-codex-skills.ps1` は Codex のみを個別設定したい場合の互換用です。
- 他PCでも同じパスに clone すれば、同じ手順書とスクリプトをそのまま使えます。

## 詳細ドキュメント

運用方針やスキル収集ルールは [SKILL_MANAGEMENT_GUIDE.md](C:\data\GitHub\skills\SKILL_MANAGEMENT_GUIDE.md) を参照してください。
