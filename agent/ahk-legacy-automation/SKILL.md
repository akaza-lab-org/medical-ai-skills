---
name: ahk-legacy-automation
description: AutoHotkey v2 (一部v1) を利用したレガシーUI/電子カルテなどのGUI自動化、及びWord VBAからのプロセス連携に関するベストプラクティス。
---

# ahk-legacy-automation

AutoHotkey (AHK) を使用して、電子カルテ (EMR) やレガシーシステムなどのGUIアプリケーションを操作・自動化する際のベストプラクティスです。
基本的に **AutoHotkey v2** を標準アプローチとしますが、v1 からの移行期であることを考慮し、v1 スクリプトを扱う場合の堅牢化ノウハウも併記しています。

医療ワークフローアプリから AHK/EMR を安全につなぐ設計や、main.ahk 常駐と *_bridge.ahk の役割分離、追加オーダーの pending/unissued 運用まで含める場合は **medical-ahk-emr-bridge も併用**する。

## 1. ファイルエンコーディングと文字化け対策

日本語環境や特定アプリ内の文字列マッチングを確実に行うための厳格なルールです。文字化け（Mojibake）は自動化失敗の大きな要因となります。

| ファイル形式 | 推奨エンコーディング | 理由 |
| :--- | :--- | :--- |
| **`.ahk` (スクリプト)** | **UTF-8 (BOM付き)** | UI上の日本語表示や正規表現での日本語マッチに必須。（※v1・v2共通の安全策） |
| **`.ini` (設定ファイル)** | **UTF-16 LE (BOM付き)** | AHKの `IniRead` / `IniWrite` が、UTF-8内の日本語キーを認識できないため。 |

## 2. AHK v1/v2 移行期・混在環境の留意事項

- **原則 v2 の仕様を採用する:** 新規に作成する処理はv2構文と関数を使用すること。(例: レガシーコマンド形式を排し関数・式として記載する)
- **v1コードを利用・保守する場合の制約:** 古いAHKバージョンやv1コード特有の制約により生じるエラーに注意。
  - **OTB（One True Brace）スタイルの回避:** `if (...) { ... } else { ... }` のような連続した構文を避け、波括弧は改行して書くこと。
  - **DPIAware呼び出し:** 高解像度モニターでの座標ズレを防ぐため、v1コードにおいてはスクリプト先頭で `DllCall("SetProcessDPIAware")` を呼び、OSの拡大率に依存しないよう振る舞う。

## 3. パフォーマンス最適化（UI待機と分岐）

通信状況や処理によって特定のウィンドウ（例：「印刷プレビュー」ダイアログや「進行・ロード」バー）が「表示される時とされない時」がある場合、単純な `WinWait` の使用はスクリプトフリーズの主な原因になります。この場合、ブロッキングなしで解消するポーリングアプローチを使用します。

### 推奨パターン：`WaitForEitherAndClick` （複数ウィンドウの同時監視）
一定期間ごとに2つ（またはそれ以上）のウィンドウが出現したかを確認し、どちらか望む画面が出現した時点で即座に反応・処理を行う設計パターンです。片方のオプション画面をスキップする遅延を最小に抑えられます。

```autohotkey
; AHK v2 スタイルの概念コード
WaitForEitherAndClick(win1, win2, timeout_sec := 5) {
    Loop (timeout_sec * 10) {
        if WinExist(win1) {
            ; win1 出現時の処理を実行
            return 1
        }
        if WinExist(win2) {
            ; win2 出現時の処理を実行
            return 2
        }
        sleepBefore := 100
        Sleep sleepBefore
    }
    return 0  ; タイムアウト
}
```

## 4. 環境非依存設計（座標・プリンタ・担当者の外部化）

解像度、Windowsの拡大率（DPI）、システム画面のレイアウトは運用PCごとに異なるため、堅牢性のために設定を分離します。

- **`config.ini` による設定値の管理**: 各要素の座標（X, Y）、タイムアウト秒数、端末固有のプリンタ名などをスクリプト内にハードコードせず、INIファイルから読み込む構造にする。
- **担当者ごとのセクション管理**: 同じPCを複数人で共有する場合、`[User_A]` や `[User_B]` のようにセクションを分け、作業パレット（各種ボタン配置など）ごと利用者単位で切り替えられるようにする。
- **設定更新の即時反映（Hot Reload）**: 設定エディタ等の別スクリプトから `PostMessage(0x0111, 65303,,, "ahk_class AutoHotkey")` を送ることで、メインスクリプトを自動再起動して設定を即座に適用させる。

## 5. 堅牢なエラーハンドリングとデバッグ

レガシー環境では「ウィンドウの移動」や「想定外のメッセージ」によって自動化が沈黙することが多いため、セルフ診断機能を設けます。

### 5.1. 座標ズレの動的検知
クリップボードコピー（`Ctrl+C`）の後に `ClipWait` を使用し、タイムアウトした場合は「座標がずれて空振りした」と判断してユーザーに通知する。
```autohotkey
A_Clipboard := ""
Click(x, y)
Send("^c")
if !ClipWait(2) {
    MsgBox("コピーに失敗しました。ウィンドウが動いたか、座標がずれている可能性があります。")
    return
}
```

### 5.2. タイムアウト時の自動ウィンドウ解析
`WinWait` やポーリングループが失敗した際、その瞬間の「アクティブウィンドウ情報（Title, Class, 最初の一行のText）」を自動でログに記録する。これにより、何が処理を妨げたのか後から特定できる。

### 5.3. 安全な中断（Esc）処理
マクロ実行中のみ `Esc` を有効化し、緊急停止ではなく「リロードによる安全な中断」を行う。普段の `Esc` 操作を邪魔しないよう `#HotIf` で制御する。
```autohotkey
global g_IsRunning := false
; (マクロ開始時に g_IsRunning := true にする)

#HotIf g_IsRunning
~Esc:: {
    LogAction("キャンセルされました")
    Reload()
}
#HotIf
```

### 5.4. 動的ホットキー設定の堅牢化
GUIや `config.ini` からホットキーを変更できる設計は便利だが、入力値の揺れや重複設定で全ホットキーが不安定になりやすい。次の4点をセットで入れる。

- **入力値の正規化:** `Ctrl+Alt+R` のような人間向け表記を `^!r` のような AHK 表記へ変換してから保存・登録する。
- **保存前バリデーション:** 空文字、不正キー名、修飾キーの誤記を保存前に止める。`none` は明示的な無効化として扱う。
- **重複ホットキーの拒否:** 同じキーを複数機能へ割り当てる場合は保存時または登録時に検出し、少なくとも片方をスキップしてログへ残す。
- **例外の可視化:** ホットキー実行関数は共通ラッパー経由で呼び、例外時は無言で止めず `operation.log` と `MsgBox` に処理名とエラー内容を出す。

最小パターン:
```autohotkey
RegisterHotkeys() {
    seen := Map()
    for item in GetActionHotkeyNames() {
        hk := NormalizeHotkeyValue(GetHotkey(item.id, item.default), item.default)
        if (hk = "" || hk = "none")
            continue
        if seen.Has(hk) {
            LogAction("重複ホットキー: " hk)
            continue
        }
        Hotkey(hk, RunAction.Bind(item.handler))
        seen[hk] := item.id
    }
}

RunAction(funcObj, *) {
    try {
        funcObj()
    } catch as e {
        LogAction("ホットキー実行失敗: " e.Message)
        MsgBox("ホットキー処理中にエラーが発生しました。")
    }
}
```

特に医療事務や電子カルテ補助の現場では、設定GUIに `Ctrl+Alt+R` と表示しつつ内部では `^!r` に統一して扱うと、運用者にも開発者にも分かりやすい。

## 6. 配布とデプロイ（セットアップ自動化）

運用環境（診察室等）への展開を容易にするため、以下の「簡単セットアップ」パターンを推奨する。

- **`setup.ahk` の作成**: 自前でインストーラーを作成し、指定の固定パス（例: `C:\DATA\AHK_Tool`）へ必要ファイルを一括コピーする。
- **設定ファイルの保護**: コピー先に既存の `config.ini` がある場合は上書きをスキップし、ユーザーが苦労して設定した座標データを守る。
- **デスクトップ・スタートアップ登録**: インストーラーから Windows のショートカット作成 (`FileCreateShortcut`) を行い、ITに詳しくない現場スタッフでも即座に運用を開始できるようにする。

### 6.1. 既存 `config.ini` を壊さないアップデート
既存端末で `config.ini` がすでに運用されている場合、新機能追加時は「上書き」ではなく「不足キーの補完」を原則とする。

- **更新前バックアップ**: `setup.ahk` で更新前の `config.ini` をインストール先 `backups/` に日時付き退避する。
- **不足キーだけ補完**: `UpgradeConfigFileToCurrent()` のようなマイグレーション関数で、新しいホットキー・座標・設定だけを `EnsureIniValue()` 相当で追加する。
- **失敗時の自動復元**: マイグレーション失敗時は直前バックアップを即時復元し、運用中の端末を壊さない。
- **新規スクリプトのコピー漏れ防止**: bridge や helper を追加したら `setup.ahk` のコピー対象へ必ず追加し、更新端末だけ機能欠落する事故を防ぐ。

### 6.2. 常駐 main.ahk とワンショット bridge の役割分離
外部アプリや QR から AHK を呼ぶ場合は、手動操作用の常駐スクリプトと、機械起動用のワンショットスクリプトを分けると安定する。
医療アプリとの連携全体設計は medical-ahk-emr-bridge を参照する。

- **`main.ahk`**: 常駐前提。ホットキー、操作パレット、担当者切替など人間操作を担当。
- **`*_bridge.ahk`**: 非常駐。引数付きで 1 回だけ動き、アプリ連携や QR 連携を担当。
- **共有ロジックは `lib/`**: 座標クリックや業務フローは共有ライブラリへ寄せる。
- **メイン専用定義を共有 lib に置かない**: bridge からは存在しない `ActionRegister()` などを共有ハンドラ表で参照すると `#Warn` の原因になる。ホットキー定義や GUI 用 callback table は `main.ahk` 側に置く。
- **起動経路の使い分け**: 人がその場で使う操作はホットキー、業務アプリ連携は bridge の直接起動を優先する。
- **設定は共通 `config.ini`**: 常駐側も bridge 側も同じ UTF-16LE `config.ini` を参照し、端末ごとの座標差だけを設定で吸収する。

## 7. Word VBA との連携・データ統合

電子カルテ側の古いWord（例：VBAマクロ）から AutoHotkey スクリプトを直接キックし、相互に連携・自動化させるための手法です。

### 5.1. VBA からの AHK の非同期起動
パスにスペースが含まれる問題を回避し、外部プロセスとなる AHK を `WScript.Shell` 経由で呼び出します。Word内だけでは完結しない自動化フローで有効です。

```vb
' VBAからのAHK起動例
Dim shell As Object
Set shell = CreateObject("WScript.Shell")
Dim ahkExe As String: ahkExe = "C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe"
Dim scriptPath As String: scriptPath = "C:\Data\Git\AHK_setting\autohotkey\main.ahk"

' パス空白回避のため、全体をダブルクォーテーションで囲んで実行
shell.Run """" & ahkExe & """ """ & scriptPath & """", 1, False
```

### 5.2. Word 内の不要な空白除去とデータクリーニング
レガシーなシステムから自動生成されたWord文書では、表示上の体裁を整えるために特殊な空白が多用されています。データを堅牢に抽出・置換するためには、取得直後の正規化が必須です。

```vb
' EN/EM/ノンブレーキング・全角スペースの除去と半角化
fullTxt = Replace(fullTxt, ChrW(8194), " ") ' EN Space
fullTxt = Replace(fullTxt, ChrW(8195), " ") ' EM Space
fullTxt = Replace(fullTxt, ChrW(12288), " ") ' 全角スペース
fullTxt = Replace(fullTxt, Chr(160), " ")   ' Non-breaking Space
' 最後に半角化して ???? などの文字化けを防止
fullTxt = StrConv(fullTxt, vbNarrow)
```

### 5.3. レガシーフォームにおける堅牢な上書き（ブックマーク・フォーム）
Word内の既存数値を安全に更新する際、単なるテキスト置換ではなく周辺にある不要文字もろとも除去してから新しいフォームフィールドを再挿入することで、古い数値の残存を回避します。

```vb
' VBAのRangeスキャンで不要な文字列や単位を消去する例
rng.MoveEndWhile Cset:=" 0123456789.　" & Chr(9) & Chr(160) & "%％", Count:=25
' 完全に消去した後で再挿入
rng.Text = "" 
doc.FormFields.Add(Range:=rng, Type:=wdFieldFormTextInput).Result = newVal
```

### 7.4. dotm テンプレート + `Document_New` + 不可視ブックマークによる新規/参照ドキュメントの識別

電子カルテから dotm でテンプレート起動するワークフローでは、参照用 old_doc と新規 new_doc が同時に開かれる状況が頻発する。`ActiveDocument` への依存は脆く、フォーカス遷移や複数ウィンドウで簡単に破綻する。

**設計パターン**: テンプレート側の `ThisDocument.Document_New` で不可視ブックマーク（例: `rk_r8v01`）を新規ドキュメントへ即時付与し、識別の単一の信頼ソースとする。

```vb
' テンプレート(.dotm)の ThisDocument モジュール
Private Sub Document_New()
    If Not ActiveDocument.Bookmarks.Exists("rk_r8v01") Then
        ActiveDocument.Bookmarks.Add "rk_r8v01", ActiveDocument.Range(0, 0)
    End If
    ' 参照ドキュメントが既に開いていれば自動コピー等を実行
    Keikakusho_CopyFromLegacy
End Sub

' 判定関数：new_doc は必ずブックマークを持つ
Public Function IsNewFormatDoc(doc As Document) As Boolean
    IsNewFormatDoc = doc.Bookmarks.Exists("rk_r8v01")
End Function

' 参照(legacy)ドキュメント探索：ブックマーク無し かつ テンプレート以外
Public Function FindLegacyDocument(docNew As Document) As Document
    Dim d As Document
    For Each d In Application.Documents
        If d.Name <> docNew.Name And Not d.IsTemplate Then
            If Not IsNewFormatDoc(d) Then
                Set FindLegacyDocument = d
                Exit Function
            End If
        End If
    Next d
End Function
```

**運用前提**: ユーザーが先に old_doc を開き、その状態で AHK が dotm から new_doc を作成する。`Document_New` 発火時点で old_doc が同一 Word プロセス内に存在するため、参照→コピーが成立する。

### 7.5. AHK → dotm 内マクロの二段呼び出し

dotm 内 VBA を端末側 `Normal.dotm` ではなくテンプレート同梱にすると、配布・バージョン管理が単純化する（git 管理・テンプレート差し替えだけで全端末に反映）。

**二段構成**:
1. **第1段（dotm 内自動）**: `Document_New` で new_doc 識別ブックマーク付与＋前段処理（参照ドキュメントからのコピー等）
2. **第2段（AHK 明示呼び出し）**: EMR から取得した本日値を、AHK が `oWord.Run "MacroName"` でマクロにパラメータ渡しして書き込む

```autohotkey
; AHK 側：new_doc 新規作成は dotm のメニュー操作で行い、その後マクロを明示呼び出し
oWord := ComObjActive("Word.Application")
oWord.Run("Keikakusho_ApplyUpdate", hba1c, sbp, dbp, weight)
```

**重要**: 第2段のマクロは `ActiveDocument` に依存させない。第1段の自動コピー後はフォーカスが EMR や old_doc に戻っている可能性があるため、`Application.Documents` を走査して `IsNewFormatDoc(d)` で対象を特定する。

```vb
Public Sub Keikakusho_ApplyUpdate(hba1c As String, sbp As String, dbp As String, weight As String)
    Dim docNew As Document, d As Document
    For Each d In Application.Documents
        If IsNewFormatDoc(d) Then Set docNew = d : Exit For
    Next d
    If docNew Is Nothing Then Exit Sub
    ' docNew に対して書き込み処理
End Sub
```

### 7.6. VBA で書き換え済みレガシードキュメントの形式自動判定

同じテンプレート由来でも、過去 VBA が `Cell.Range.Text = ""` 等でセル内容を完全再構築していると、フォームフィールド数・段落構造が変わり、原形用の読み取りロジックが破綻する。

**判定パターン**: 識別しやすい行（例: 身長/体重行）の `FormFields.Count` で原形/書換済を切り分け、読み取り関数を分岐する。

```vb
Private Function IsSimplifiedFormat(docOld As Document) As Boolean
    ' 身長/標準体重 行のフィールド数で判別
    Dim rng As Range
    Set rng = FindRowByLabel(docOld, "身長")
    If rng Is Nothing Then Exit Function
    IsSimplifiedFormat = (rng.FormFields.Count = 4)  ' 原形は5以上
End Function

Private Sub CopyGoalSectionInternal(docOld As Document, docNew As Document)
    If IsSimplifiedFormat(docOld) Then
        CopyGoalSectionSimplified docOld, docNew
        Exit Sub
    End If
    ' 原形ロジック ...
End Sub
```

**設計指針**: 「過去 VBA が何をしたか」を文書外（フラグ・タグ）で持たせるより、文書構造そのものから判別すると、過去の処理経路に依らず堅牢になる。

### 7.7. VBA `.bas` の UTF-8 / CP932 二重管理

VBE のインポート（`File → Import File`）は CP932 を要求するが、git 管理・コードレビューには UTF-8 が必須。これを両立させるため、ソースと配布物を分離する。

| ファイル | エンコーディング | 用途 | git |
|---|---|---|---|
| `KeikakushoAutomation.bas` | UTF-8 | git 管理ソース、コードレビュー対象 | 追跡 |
| `KeikakushoAutomation_import.bas` | CP932 | VBE インポート用配布物 | gitignore |
| `KeikakushoAutomation_paste.txt` | UTF-8 | VBE に手動貼り付けする場合のコピー元 | 追跡 |

**再生成コマンド（PowerShell）**:

```powershell
$src = "vba\KeikakushoAutomation.bas"
$dst = "vba\KeikakushoAutomation_import.bas"
$bytes = [System.Text.Encoding]::GetEncoding(932).GetBytes((Get-Content $src -Encoding UTF8 -Raw))
[System.IO.File]::WriteAllBytes($dst, $bytes)
```

**運用ルール**:
- 日本語文字列リテラルは可能な限り `U(34880, 22311, 30446, 27161)` のような Unicode コードポイント連結関数経由にし、CP932 往復で壊れにくくする。
- インポート手順書には必ず「`_import.bas` を使うこと、`.bas`（UTF-8）を直接インポートしない」と明記する。


