import re
import os
import time
import base64
import datetime
from playwright.sync_api import sync_playwright

def sanitize_filename(name):
    return re.sub(r'[\\/*?:"<>|]', "", name)

def parse_date(date_str):
    if not date_str: return None
    try:
        clean = re.sub(r'[年月日]', '/', date_str.strip())
        clean = clean.split('(')[0].strip()
        # Handle cases like "2025/01/01 10:00"
        clean = clean.split(' ')[0]
        return datetime.datetime.strptime(clean, "%Y/%m/%d")
    except:
        return None

def get_user_config():
    print("\n=== 設定 ===")
    
    # 1. Skip check
    skip_filled = False
    while True:
        ans = input("作成済みはスキップしますか？ (Y/N) > ").strip().upper()
        if ans == 'Y':
            skip_filled = True
            break
        elif ans == 'N':
            skip_filled = False
            break
    
    # 2. Date Filter check
    start_str = None
    end_str = None
    
    while True:
        ans = input("期間指定しますか？ (Y/N) > ").strip().upper()
        if ans == 'N':
            break
        elif ans == 'Y':
            # Start Date
            while True:
                raw = input("（１）開始日いつから？ (例: 2026/01/05) > ").strip()
                try:
                    dt = datetime.datetime.strptime(raw, "%Y/%m/%d")
                    start_str = dt.strftime("%Y%m%d")
                    break
                except:
                    print("  ※正しい形式(YYYY/MM/DD)で入力してください。")
            
            # End Date
            while True:
                raw = input("（２）終了日いつまで？ (例: 2026/02/01, 指定しない場合はEnter) > ").strip()
                if raw == "":
                    dt = datetime.datetime.now()
                    end_str = dt.strftime("%Y%m%d")
                    print(f"  ※本日({dt.strftime('%Y/%m/%d')})を終了日とします。")
                    break
                try:
                    dt = datetime.datetime.strptime(raw, "%Y/%m/%d")
                    end_str = dt.strftime("%Y%m%d")
                    break
                except:
                    print("  ※正しい形式(YYYY/MM/DD)で入力してください。")
            break
            
    return skip_filled, start_str, end_str

def main():
    RECEIPT_NAME = "赤座　至"
    FILENAME_PREFIX = "tobu_akaza_"
    OUTPUT_DIR = os.path.join(os.getcwd(), "receipts")
    
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    print("=== トブチケ領収書ダウンローダー v1.2.1 (乗車日対応版) ===")
    
    SKIP_IF_FILLED, TARGET_DATE_START, TARGET_DATE_END = get_user_config()
    
    print("\n設定内容:")
    print(f"- 作成済みスキップ: {'ON' if SKIP_IF_FILLED else 'OFF'}")
    if TARGET_DATE_START or TARGET_DATE_END:
        s = TARGET_DATE_START if TARGET_DATE_START else "なし"
        e = TARGET_DATE_END if TARGET_DATE_END else "なし"
        print(f"- 期間指定（乗車日基準）: {s} ～ {e}")
    else:
        print("- 期間指定: なし（全期間）")
    
    print("\nブラウザを起動しています...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-popup-blocking"])
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()
        page.on("dialog", lambda d: d.accept())

        try:
            page.goto("https://tobuchike.jp/shop/customer/tickethistory.aspx")
        except:
            pass

        print("\n" + "="*60)
        print("【手動操作】")
        print("1. ログインしてください。")
        print("2. 「履歴一覧」ページが表示されている状態で...")
        print("3. このターミナルで Enter キーを押してください。")
        print("="*60 + "\n")

        input("準備OKなら Enter を押してください >>> ")
        
        print("リンクを解析中...")
        detail_urls = []
        try:
            links = page.locator("a").all()
            for link in links:
                href = link.get_attribute("href")
                if href and "tickethistorydetail.aspx" in href:
                    full_url = "https://tobuchike.jp" + href if href.startswith("/") else href
                    if full_url not in detail_urls:
                        detail_urls.append(full_url)
        except Exception as e:
            print(f"リンク解析エラー: {e}")

        total = len(detail_urls)
        print(f"合計 {total} 件の履歴が見つかりました。")

        start_dt = datetime.datetime.strptime(TARGET_DATE_START, "%Y%m%d") if TARGET_DATE_START else None
        end_dt = datetime.datetime.strptime(TARGET_DATE_END, "%Y%m%d") if TARGET_DATE_END else None

        success_count = 0
        skip_count = 0
        
        for i, url in enumerate(detail_urls):
            print(f"\n[{i+1}/{total}] 確認中: {url}")
            try:
                page.goto(url)
                page.wait_for_load_state("networkidle")
                
                # Check Address Input
                name_input = page.locator("#receipt_address")
                if name_input.count() == 0:
                    print("  宛名入力欄が見つかりません。スキップ。")
                    continue
                
                current_address = name_input.input_value()
                address_is_filled = (current_address.strip() != "")
                
                # --- DATE DETECTION (HTML Parsing) ---
                ride_date_obj = None
                purchase_date_obj = None
                
                try:
                    dts = page.locator("dt").all()
                    dds = page.locator("dd").all()
                    count = min(len(dts), len(dds))
                    
                    for k in range(count):
                        label = dts[k].inner_text().strip()
                        val = dds[k].inner_text().strip()
                        dt_parsed = parse_date(val)
                        
                        if dt_parsed:
                            if "乗車" in label or "利用" in label:
                                ride_date_obj = dt_parsed
                            elif "購入" in label or "受付" in label:
                                purchase_date_obj = dt_parsed
                except:
                    pass
                
                # Selection: Use Ride Date preferentially
                check_date = ride_date_obj if ride_date_obj else purchase_date_obj
                date_type = "乗車日" if ride_date_obj else ("購入日" if purchase_date_obj else "不明")
                
                if check_date:
                    print(f"  {date_type}: {check_date.strftime('%Y/%m/%d')}")
                else:
                    print("  日付情報の取得に失敗")

                # --- FILTER LOGIC ---
                is_target = True
                logic_msg = ""
                
                if start_dt or end_dt:
                    if not check_date:
                         print("  ※日付不明のため、念のため処理対象とします。")
                    else:
                        in_range = True
                        if start_dt and check_date < start_dt: in_range = False
                        if end_dt and check_date > end_dt: in_range = False
                        
                        if in_range:
                            is_target = True
                            logic_msg = "期間内対象"
                        else:
                            is_target = False
                            logic_msg = f"期間外 ({check_date.strftime('%Y/%m/%d')})"
                else:
                    if SKIP_IF_FILLED and address_is_filled:
                        is_target = False
                        logic_msg = "宛名済みスキップ"

                if not is_target:
                    print(f"  -> {logic_msg}")
                    skip_count += 1
                    continue

                if current_address != RECEIPT_NAME:
                    name_input.fill(RECEIPT_NAME)
                    print(f"  宛名修正: {RECEIPT_NAME}")

                issue_button = page.locator("#issue_button")
                if issue_button.count() == 0:
                    print("  ボタンなし")
                    continue
                
                print("  発行＆PDF化...")
                try:
                    with page.expect_popup() as popup_info:
                        issue_button.click()
                    
                    popup = popup_info.value
                    popup.wait_for_load_state("load")
                    
                    # Filename: Prefer HTML date, fallback to extract
                    file_date_str = check_date.strftime("%Y%m%d") if check_date else datetime.datetime.now().strftime("%Y%m%d")
                    
                    # Optional: Double check popup content?
                    # The user said "Judge by history.html", so we trust HTML date.
                    
                    filename = f"{FILENAME_PREFIX}{file_date_str}.pdf"
                    save_path = os.path.join(OUTPUT_DIR, filename)

                    # Deduplicate in case of multiple rides on same day
                    if os.path.exists(save_path):
                        c = 1
                        while True:
                            nn = f"{FILENAME_PREFIX}{file_date_str}_{c}.pdf"
                            np = os.path.join(OUTPUT_DIR, nn)
                            if not os.path.exists(np):
                                save_path = np
                                filename = nn
                                break
                            c += 1

                    client = popup.context.new_cdp_session(popup)
                    res = client.send("Page.printToPDF", {"format": "A4", "printBackground": True})
                    data = base64.b64decode(res["data"])
                    with open(save_path, "wb") as f:
                        f.write(data)
                    
                    print(f"  ★保存成功: {filename}")
                    success_count += 1
                    popup.close()

                except Exception as e:
                    print(f"  発行エラー: {e}")

            except Exception as e:
                print(f"  エラー: {e}")

        print("\n" + "="*60)
        print(f"完了: 保存 {success_count} / スキップ {skip_count}")
        input("終了するには Enter を押してください...")
        browser.close()

if __name__ == "__main__":
    main()
