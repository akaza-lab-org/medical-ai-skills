---
name: windows-portable-python-distribution
description: Windows端末でシステムインストールを避けつつ、embeddable Python・PowerShell GUI・配布用ZIPを使った no-install 配布を設計・実装・検証するときに使う。配布元PCだけで setup.bat を実行し、端末では run.bat のみを実行する構成、dist/ と logs/ を含む配布パッケージ作成、tkinter 不足時の WinForms 代替が必要なときに有効。
---

# Windows Portable Python Distribution

## Use This Skill For

- 制限された Windows 端末で、システムへの Python / pip / ライブラリのインストールを避けたいとき
- 配布元PCだけで依存を固め、端末では `run.bat` のみで動かしたいとき
- `setup.bat` で embeddable Python を取得し、`dist/` に配布ZIPまで自動生成したいとき
- 同梱 Python に `tkinter` がないため、PowerShell WinForms を GUI フロントに使いたいとき

## Workflow

1. 役割を分離する。
- 配布元PCのみが `setup.bat` を実行する。
- 端末では `run.bat` / `run_auto.bat` だけを使う。
- 実行時ダウンロードや `pip install` を端末側に入れない。

2. Python 実行系をフォルダ内に閉じる。
- `python\python.exe` を唯一の Python 実行入口にする。
- `PYTHONPATH` は `python\Lib\site-packages` と `python\Lib` を優先する。
- システム Python へのフォールバックは、制限端末向け配布では原則入れない。

3. `setup.bat` を配布元PC専用にする。
- embeddable Python を `python\` へ展開する。
- `python3*._pth` を編集して `import site` と `Lib\site-packages` を有効化する。
- 依存は `python\Lib\site-packages` へ `--target` で入れる。
- 完了後に `dist\<package_name>\` と `dist\<package_name>.zip` を作る。
- 実行ログは `logs\setup_*.log` に保存する。

4. GUI は標準機能を優先する。
- 同梱 Python に `tkinter` がない可能性を前提にする。
- 手動起動用GUIは `run_gui.ps1` などの PowerShell WinForms で実装する。
- 実行中の Yes/No や完了通知は、Windows 標準ダイアログを優先し、無理なら CLI にフォールバックする。

5. 配布物を最小化する。
- 含める: `run.bat`, `run_auto.bat`, GUI ランチャー, メインスクリプト, `.env.example`, 必要なら `.env`, `python\`, 空の `download\`
- 含めない: `.git`, 開発用スクリーンショット, キャッシュ, 開発メモ

## Validation Checklist

1. `setup.bat` 実行後に `python\python.exe` が存在する。
2. `dist\...zip` が生成される。
3. `logs\setup_*.log` が生成され、失敗時の箇所が追える。
4. 端末想定で `run.bat` 実行時に追加インストールが走らない。
5. `tkinter` がない環境でも手動起動GUIが開く。
6. `run_auto.bat` は GUI なしで保存済み設定を使う。

## Implementation Notes

- `setup.bat` は `cmd.exe` 互換を優先し、ASCII 中心で書く。
- PowerShell 呼び出しは `-NoProfile -ExecutionPolicy Bypass` を明示する。
- 端末制約が強い案件では、`setup.bat` を端末で実行する前提にしない。
