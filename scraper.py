import csv
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

# =========================
# 設定
# =========================
URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=208"
DATE = "20260520"
OUTPUT_FILE = "trading_value_ranking_20260520.csv"

HEADER = [
    "日付","No","コード","銘柄名","市場",
    "株価(百万円)","前日比","前日比(%)",
    "売買代金","PER","PBR","利回り"
]

# =========================
# CSV初期化
# =========================
def init_csv():
    if not os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(HEADER)

def append_rows(rows):
    with open(OUTPUT_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

# =========================
# 208ページ専用パース
# =========================
def parse_raw(raw, no):
    parts = raw.split()

    if len(parts) < 9:
        return None

    return [
        DATE,
        no,
        parts[1],  # コード
        parts[0],  # 銘柄名
        parts[2],  # 市場
        parts[3],  # 株価
        parts[4],  # 前日比
        parts[5],  # 前日比%
        parts[6],  # 売買代金
        parts[7],  # PER
        parts[8],  # PBR
        parts[9] if len(parts) > 9 else ""
    ]

# =========================
# Chrome設定（軽量・安定）
# =========================
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")

    return webdriver.Chrome(options=options)

# =========================
# 208ページ取得（raw抽出）
# =========================
def fetch_page208(driver):
    driver.get(URL)
    time.sleep(3)

    raw_list = []

    # 最終ページはテーブル構造が崩れるので td を使わず text 取得
    rows = driver.find_elements(By.CSS_SELECTOR, "tr")

    for r in rows:
        txt = r.text.strip()

        # ヘッダー・空行除外
        if not txt:
            continue
        if "銘柄" in txt and "市場" in txt:
            continue
        if "前へ" in txt or "次へ" in txt:
            continue
        if "件 /" in txt:
            continue

        # それっぽいデータだけ残す（コードが数字 or 4桁以上）
        if len(txt.split()) < 6:
            continue

        raw_list.append(txt)

    return raw_list

# =========================
# メイン処理
# =========================
def main():
    print("===== START (208 PAGE ONLY) =====")

    init_csv()

    driver = create_driver()

    try:
        raw_list = fetch_page208(driver)

        print(f"[INFO] raw rows: {len(raw_list)}")

        rows = []
        start_no = 4141  # 最終ページ想定

        for i, raw in enumerate(raw_list):
            parsed = parse_raw(raw, start_no + i)
            if parsed:
                rows.append(parsed)

        append_rows(rows)

        print(f"[DONE] saved rows: {len(rows)}")
        print(f"[FILE] {OUTPUT_FILE}")

    finally:
        driver.quit()

    print("===== END =====")


if __name__ == "__main__":
    main()
