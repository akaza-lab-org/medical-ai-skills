from playwright.sync_api import sync_playwright
import time
import os

def main():
    print("ブラウザを起動しています...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        print("トブチケのログインページに移動します...")
        try:
            page.goto("https://tobuchike.jp/shop/customer/tickethistory.aspx")
        except Exception:
            pass

        print("\n" + "="*50)
        print("【重要】")
        print("1. ログインしてください。")
        print("2. 履歴一覧から、「領収書を発行したい」任意の履歴の「詳細ボタン」クリックして、詳細ページを開いてください。")
        print("   (URLが tickethistorydetail.aspx?order_id=... となるページです)")
        print("3. 詳細ページが開いたら、このターミナルで Enter キーを押してください。")
        print("="*50 + "\n")

        input("詳細ページが表示されたら、Enter キーを押してください...")

        print("詳細ページの内容を取得しています...")
        try:
            page.wait_for_load_state("networkidle")
            content = page.content()
            
            # Save to user workspace
            target_file = os.path.join(os.getcwd(), "tobuchike_detail.html")
            
            with open(target_file, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"HTMLを '{target_file}' に保存しました。")
            print("このファイルの中身をエージェント（私）に共有してください。")
        except Exception as e:
             print(f"HTMLの保存に失敗しました: {e}")
        
        print("ブラウザを閉じます...")
        browser.close()

if __name__ == "__main__":
    main()
