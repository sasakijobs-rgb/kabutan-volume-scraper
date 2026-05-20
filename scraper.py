import re
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

DATE = "20260520"
BASE_URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page="
OUTPUT_FILE = f"trading_value_ranking_{DATE}.csv"


# =========================
# Driver生成（安定版）
# =========================
def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")

    return webdriver.Chrome(options=options)


# =========================
# ページ取得
# =========================
def load(driver, page):
    url = BASE_URL + str(page)
    driver.get(url)
    time.sleep(2)


# =========================
# 1ページ目（通常DOM）
# =========================
def parse_page1(driver):
    load(driver, 1)

    rows = []
    trs = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    no = 1

    for tr in trs:
        try:
            th = tr.find_element(By.TAG_NAME, "th").text
            tds = tr.find_elements(By.TAG_NAME, "td")

            parts = th.split()
            name = parts[0]
            code = parts[1]
            market = parts[2]

            price = tds[0].text.strip()

            change_parts = tds[1].text.split()
            change = change_parts[0]
            change_pct = change_parts[1] if len(change_parts) > 1 else ""

            volume = tds[2].text.strip()
            per = tds[3].text.strip()
            pbr = tds[4].text.strip()
            yield_ = tds[5].text.strip()

            rows.append([
                DATE, no, code, name, market,
                price, change, change_pct,
                volume, per, pbr, yield_
            ])
            no += 1

        except:
            continue

    return rows


# =========================
# 最終ページ（崩れ対応）
# =========================
def parse_last(driver, page):
    load(driver, page)

    html = driver.page_source
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"<.*?>", "", text)

    lines = text.split("\n")

    rows = []
    no = 4141  # 固定（必要なら自動化可）

    for line in lines:
        line = line.strip()

        # 銘柄行フィルタ（重要）
        if not re.search(r"\d{4}", line):
            continue

        parts = line.split()

        # 最低9要素ないものは除外
        if len(parts) < 9:
            continue

        try:
            name = parts[0]
            code = parts[1]
            market = parts[2]
            price = parts[3]
            change = parts[4]
            change_pct = parts[5]
            volume = parts[6]
            per = parts[7]
            pbr = parts[8]
            yield_ = parts[9] if len(parts) > 9 else ""

            rows.append([
                DATE, no, code, name, market,
                price, change, change_pct,
                volume, per, pbr, yield_
            ])
            no += 1

        except:
            continue

    return rows


# =========================
# CSV出力（固定フォーマット）
# =========================
def save_csv(rows):
    header = [
        "日付","No","コード","銘柄名","市場",
        "株価(百万円)","前日比","前日比(%)",
        "売買代金","PER","PBR","利回り"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# =========================
# MAIN
# =========================
def main():
    print("===== START =====")

    driver = create_driver()

    all_rows = []

    # 1ページ目
    print("[PAGE 1]")
    rows1 = parse_page1(driver)
    print("page1 rows:", len(rows1))
    all_rows.extend(rows1)

    # 最終ページ（208固定）
    print("[PAGE 208]")
    rows_last = parse_last(driver, 208)
    print("page208 rows:", len(rows_last))
    all_rows.extend(rows_last)

    driver.quit()

    save_csv(all_rows)

    print("===== DONE =====")
    print("file:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
