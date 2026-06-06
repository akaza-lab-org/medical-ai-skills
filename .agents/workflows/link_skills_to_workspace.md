---
description: ワークスペース（現在のプロジェクト）に共通スキルフォルダ（.agents）をリンクします
---

# `c:\Data\skills` のスキルをこのプロジェクトに読み込むワークフロー

このワークフローは、現在開いている開発プロジェクトの直下に `.agents` フォルダを作成し、それが `c:\Data\skills\agent` を参照するようにシンボリックリンクを張ります。

// turbo-all
1. 以下のコマンドを実行して、ワークスペースに `.agents` フォルダが存在するか確認し、なければシンボリックリンクを作成します。（PowerShellで実行）
```powershell
$targetPath = Join-Path $PWD ".agents"
$sourcePath = "C:\Data\skills\agent"

if (Test-Path $targetPath) {
    Write-Host ".agents folder already exists in the workspace!" -ForegroundColor Yellow
} else {
    cmd /c mklink /J "$targetPath" "$sourcePath" | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully linked .agents to C:\Data\skills\agent" -ForegroundColor Green
    } else {
        Write-Host "Failed to create link. Please check permissions." -ForegroundColor Red
    }
}
```
2. エージェントに「利用可能なスキル一覧を確認して」と指示してください。
