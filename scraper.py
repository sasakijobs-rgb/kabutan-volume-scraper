# scraper_207.py
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import csv
import datetime
import re

def main():
    print("===== START (207 PAGE ONLY) =====")
    
    # 日付
    today = datetime.datetime.now().strftime("%Y%m%d")
    
    # Chrome 設定
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # GUIなし
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=chrome_options
    )
    
    url = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=207"
    driver.get(url)
    
    # 行データ取得
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
    print(f"[INFO] raw rows: {len(rows)}")
    
    output = []
    start_no = 4141  # 207ページの最初の順位
    
    for idx, row in enumerate(rows):
        # 銘柄名、コード、市場
        th = row.find_element(By.TAG_NAME, "th")
        name = th.find_element(By.TAG_NAME, "p").text.strip()
        code_market = th.find_element(By.CSS_SELECTOR, "div").text.strip().split()
        if len(code_market) == 2:
            code, market = code_market
        else:
            code = code_market[0]
            market = ""
        
        # 株価〜利回りまで
        tds = row.find_elements(By.TAG_NAME, "td")
        stock_price = tds[0].text.strip().replace(",", "")
        prev_diff = tds[1].text.strip().replace("\n", " ")
        trade_value = tds[2].text.strip()
        per = tds[4].text.strip()
        pbr = tds[5].text.strip()
        yld = tds[6].text.strip()
        
        # raw_data 作成
        raw_data = f"{name} {code} {market} {stock_price} {prev_diff} {trade_value} {per} {pbr} {yld}"
        output.append([today, start_no + idx, raw_data])
    
    driver.quit()
    
    # CSV 書き込み
    csv_file = "trading_value_ranking_20260521.csv"
    with open(csv_file, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["日付", "順位", "raw_data"])
        writer.writerows(output)
    
    print(f"[DONE] saved rows: {len(output)}")
    print(f"[FILE] {csv_file}")
    print("===== END =====")

if __name__ == "__main__":
    main()
