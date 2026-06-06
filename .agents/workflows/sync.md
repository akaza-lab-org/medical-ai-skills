---
description: 共通スキルリポジトリ（c:\Data\skills）を最新状態に同期（git pull）します
---

# スキルの自動同期 (Sync) ワークフロー

// turbo-all
1. 以下のコマンドで、スキルの同期スクリプトをバックグラウンド実行します。
```powershell
Start-Process -FilePath "C:\Data\skills\automation\sync_skills.bat" -WindowStyle Hidden
Write-Host "Started sync in background."
```
2. エージェントに「バックグラウンドで同期を開始しました。最新のスキル一覧を確認して」と報告させてください。
