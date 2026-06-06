---
name: labtechsc-portable-edge-distribution
description: LabtechSC ver3 環境向けに、端末でセットアップせず「フォルダをコピーして run.bat 実行のみ」で動かす軽量配布を設計・実装・検証するスキル。電子カルテ端末でローカルインストール禁止、ネット通信可、Chrome/Edge 既存利用の条件があるときに使う。
---

# LabtechSC Portable Edge Distribution

## Overview

LabtechSC ver3 端末向けの配布を、`no install` と `lightweight` の両立で標準化する。Playwright 専用ブラウザは同梱せず、端末既存の Edge/Chrome を使う。

## Workflow

1. 配布条件を固定する。
- 端末では `setup.bat` や `pip install` を実行しない。
- ネット通信は許可されるが、実行時ダウンロードは行わない。
- ブラウザは `msedge -> chrome` の順で起動し、どちらもない場合は明示エラー終了する。

2. 実行バッチを端末専用にする。
- `run.bat` は同梱 `python\python.exe` のみを使う。
- システム Python / py launcher へのフォールバックを入れない。
- `python\python.exe` が存在しない場合は「配布元PCで setup.bat を実行してください」と表示して終了する。
- `PYTHONPATH` で `python\Lib\site-packages` を参照し、不足時は「再配布が必要」と表示して終了する。

3. Python 本体コードを軽量配布前提にする。
- Playwright 起動は `pw.chromium.launch(channel="msedge")` を最優先にする。
- 次に `channel="chrome"` を試す。
- Playwright Chromium (`playwright install chromium`) 前提の処理は入れない。

4. 配布元PCと端末の役割を分離する。
- 配布元PCのみで `setup.bat` を実行する。
- 端末は配布フォルダを受け取り `run.bat` 実行のみとする。

5. `setup.bat` で配布パッケージを作成する（配布元PCのみ）。
- Python 3.11.9 embeddable を自動ダウンロードし `python\` へ展開する。
- `python311._pth` を編集して `import site` を有効化し `Lib\site-packages` を追加する。
  - 編集は PowerShell の `Get-ChildItem` でファイルを特定してから行う（batch の `for` ループでは引用符付きワイルドカードが展開されないため）。
- pip をブートストラップし `requirements.txt` を `python\Lib\site-packages` へインストールする。
- 完成した `python\` フォルダは git 管理外（`.gitignore`）とする。

6. 最終配布フォルダを確認する。
- 必須: `run.bat`, `download_bookings.py`, `.env`（または投入手順）, `python\python.exe`, `python\Lib\site-packages\playwright`, `python\Lib\site-packages\dotenv`
- 省略: `browsers\`（Playwright 専用 Chromium）
- 推奨: `download\`（空で可）

## Validation Checklist

1. 配布元PCで `setup.bat` を実行し `python\python.exe` が生成されることを確認する。
2. 端末想定で `run.bat` を実行し、`pip install` が走らないことを確認する。
3. Edge あり環境で正常起動することを確認する。
4. Edge なし Chrome あり環境でフォールバック起動することを確認する。
5. Edge/Chrome なし環境で、原因が分かるエラーメッセージで終了することを確認する。
6. `python\python.exe` を削除した状態で `run.bat` を実行し、再配布を促すエラーが表示されることを確認する。
7. CSV 保存と既存ローテーション処理が従来どおり動くことを確認する。

## Output Template

配布手順を報告するときは以下を含める。

- 前提条件: 「端末セットアップなし」「ネット通信可」「Chrome/Edge 既存利用」
- 配布元PC手順: 「setup.bat を実行してパッケージ作成 → フォルダをコピー」
- 配布構成: 同梱するフォルダと除外するフォルダ
- 実行方法: 「端末は run.bat のみ」
- 障害時対応: Edge/Chrome 未導入時、同梱ライブラリ不足時、`python.exe` 欠損時の対処
