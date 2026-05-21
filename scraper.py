# scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv
import datetime


def main():
    print("===== START (207 PAGE ONLY) =====")

    # 日付
    today = datetime.datetime.now().strftime("%Y%m%d")

    # Chrome 設定
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # Selenium Manager を使用
    driver = webdriver.Chrome(options=chrome_options)

    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        "?market=all&page=207"
    )

    driver.get(url)

    # テーブル読み込み待機
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "table tbody tr")
        )
    )

    # 行取得
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    print(f"[INFO] raw rows: {len(rows)}")

    output = []

    # 207ページ開始順位
    start_no = 4141

    for idx, row in enumerate(rows):

        try:
            # th がない行をスキップ
            th = row.find_element(By.TAG_NAME, "th")

        except Exception:
            print(f"[SKIP] row {idx} has no th")
            continue

        try:
            # 銘柄名
            name = (
                th.find_element(By.TAG_NAME, "p")
                .text
                .strip()
            )

            # コード + 市場
            code_market = (
                th.find_element(By.CSS_SELECTOR, "div")
                .text
                .strip()
                .split()
            )

            if len(code_market) >= 2:
                code = code_market[0]
                market = code_market[1]
            elif len(code_market) == 1:
                code = code_market[0]
                market = ""
            else:
                code = ""
                market = ""

            # td 群
            tds = row.find_elements(By.TAG_NAME, "td")

            # td不足行をスキップ
            if len(tds) < 7:
                print(f"[SKIP] row {idx} td不足")
                continue

            stock_price = (
                tds[0]
                .text
                .strip()
                .replace(",", "")
            )

            prev_diff = (
                tds[1]
                .text
                .strip()
                .replace("\n", " ")
            )

            trade_value = tds[2].text.strip()
            per = tds[4].text.strip()
            pbr = tds[5].text.strip()
            yld = tds[6].text.strip()

            # raw_data
            raw_data = (
                f"{name} "
                f"{code} "
                f"{market} "
                f"{stock_price} "
                f"{prev_diff} "
                f"{trade_value} "
                f"{per} "
                f"{pbr} "
                f"{yld}"
            )

            # 順位は output 数基準
            rank_no = start_no + len(output)

            output.append([
                today,
                rank_no,
                raw_data
            ])

            print(f"[OK] {rank_no} {name}")

        except Exception as e:
            print(f"[ERROR] row {idx}: {e}")
            continue

    driver.quit()

    # CSV保存
    csv_file = f"trading_value_ranking_{today}.csv"

    with open(
        csv_file,
        mode="w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "日付",
            "順位",
            "raw_data"
        ])

        writer.writerows(output)

    print(f"[DONE] saved rows: {len(output)}")
    print(f"[FILE] {csv_file}")
    print("===== END =====")


if __name__ == "__main__":
    main()
