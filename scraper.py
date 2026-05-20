import csv
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL_TEMPLATE = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page={}"

OUTPUT_FILE = "trading_value_ranking_20260520.csv"


# =========================
# クリーン
# =========================
def clean(text):
    return text.replace("\n", " ").replace("\t", " ").strip()


# =========================
# 行判定（銘柄コード4桁）
# =========================
def is_data_row(cells):
    for c in cells:
        if c.isdigit() and len(c) == 4:
            return True
    return False


# =========================
# ページ取得
# =========================
def fetch_page(driver, page):
    url = URL_TEMPLATE.format(page)
    print(f"\n[PAGE] {page} / {url}")

    driver.get(url)
    time.sleep(2)

    rows = driver.find_elements(By.TAG_NAME, "tr")

    print(f"[INFO] rows detected: {len(rows)}")

    result = []

    for r in rows:
        ths = r.find_elements(By.TAG_NAME, "th")
        tds = r.find_elements(By.TAG_NAME, "td")

        cells = [clean(x.text) for x in ths + tds if x.text.strip()]

        if len(cells) < 6:
            continue

        if not is_data_row(cells):
            continue

        result.append(cells)

    return result


# =========================
# メイン
# =========================
def run():

    print("===== START =====")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    pages = [1, 208]

    all_data = []

    for page in pages:
        data = fetch_page(driver, page)

        print(f"[RESULT] page {page} rows: {len(data)}")

        for row in data:
            all_data.append([page] + row)

    driver.quit()

    # =========================
    # CSV出力
    # =========================
    header = [
        "日付",
        "No",
        "コード",
        "銘柄名",
        "市場",
        "株価(百万円)",
        "前日比",
        "前日比(%)",
        "売買代金",
        "PER",
        "PBR",
        "利回り"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        writer.writerow(header)

        for row in all_data:
            # 安全に長さ補正
            page = row[0]
            data = row[1:]

            data = data[:11] + [""] * (11 - len(data))

            writer.writerow([page] + data)

    print("\n===== DONE =====")
    print(f"file: {OUTPUT_FILE}")
    print(f"total rows: {len(all_data)}")
    print("===== END =====")


if __name__ == "__main__":
    run()
