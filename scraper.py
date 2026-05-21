# scraper.py

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import csv
import datetime
import time


def main():

    print("===== START =====")

    today = datetime.datetime.now().strftime("%Y%m%d")

    chrome_options = Options()

    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    # User-Agent追加（重要）
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/125.0 Safari/537.36"
    )

    driver = webdriver.Chrome(options=chrome_options)

    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        "?market=all&page=207"
    )

    driver.get(url)

    # 読み込み待機
    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located(
            (By.TAG_NAME, "table")
        )
    )

    # 少し待つ（Kabutan対策）
    time.sleep(3)

    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table tbody tr"
    )

    print(f"[INFO] raw rows: {len(rows)}")

    output = []

    start_no = 4141

    for idx, row in enumerate(rows):

        try:

            # 銘柄リンク有無で判定
            stock_link = row.find_elements(
                By.CSS_SELECTOR,
                'a[href*="/stock/?code="]'
            )

            if not stock_link:
                print(f"[SKIP] row {idx} no stock link")
                continue

            # th
            th = row.find_element(By.TAG_NAME, "th")

            # 銘柄名
            name = (
                th.find_element(By.TAG_NAME, "p")
                .text
                .strip()
            )

            # コード・市場
            div_text = (
                th.find_element(By.TAG_NAME, "div")
                .text
                .strip()
            )

            parts = div_text.split()

            if len(parts) >= 2:
                code = parts[0]
                market = parts[1]
            elif len(parts) == 1:
                code = parts[0]
                market = ""
            else:
                code = ""
                market = ""

            # td
            tds = row.find_elements(By.TAG_NAME, "td")

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

    csv_file = (
        f"trading_value_ranking_{today}.csv"
    )

    with open(
        csv_file,
        "w",
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
