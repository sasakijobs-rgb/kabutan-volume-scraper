# =========================
# 制御py(ここから他pyを実行する)
# scraper.py
# (１ページが前回の内容と同じなら中断）
# →cleanup.py
# (ファイルが150個以上は削除)
# →data2csv.py
# (株探のモバイル版からデータを取得）
# →merge.py
# (最初だけ見出しをセット＆２ファイル目以降はデータのみ)
# =========================

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

import csv
import datetime
import os
import time
import re
from datetime import timedelta, timezone


def log(msg):
    print(msg)


# =========================
# 総件数取得
# =========================
def get_total_count(text):

    match = re.search(r"/\s*([0-9,]+)件中", text)

    if match:
        return int(match.group(1).replace(",", ""))

    return None


# =========================
# 1ページ取得
# =========================
def parse_page(driver, page, start_no, today):

    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        f"?market=all&page={page}"
    )

    driver.get(url)

    time.sleep(1.5)  # ★安定化重要

    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    output = []

    for row in rows:

        text = row.text.strip()

        if not text:
            continue

        # =========================
        # S / K 除去
        # =========================
        text = text.replace(" S ", " ")
        text = text.replace(" K ", " ")

        parts = text.split()

        # =========================
        # % / 倍 結合
        # =========================
        merged = []

        for p in parts:

            if p in ["%", "倍"]:
                if merged:
                    merged[-1] += p
            else:
                merged.append(p)

        parts = merged

        # =========================
        # データチェック
        # =========================
        if len(parts) < 10:
            continue

        name = parts[0]
        code = parts[1]
        market = parts[2]
        stock_price = parts[3]
        diff_price = parts[4]
        diff_percent = parts[5]
        trade_value = parts[6]
        per = parts[7]
        pbr = parts[8]
        yld = parts[9]

        # 数値チェック（崩れ防止）
        if not stock_price.replace(",", "").replace("-", "").isdigit():
            continue

        rank_no = start_no + len(output)

        output.append([
            today,
            rank_no,
            name,
            code,
            market,
            stock_price,
            diff_price,
            diff_percent,
            trade_value,
            per,
            pbr,
            yld
        ])

    return output


# =========================
# main
# =========================
def main():

    JST = timezone(timedelta(hours=9))
    start_time = datetime.datetime.now(JST)

    today = start_time.strftime("%Y%m%d")

    os.makedirs("output", exist_ok=True)

    csv_file = f"output/trading_value_ranking_{today}.csv"

    log("===== START =====")

    # =========================
    # Chrome設定
    # =========================
    options = Options()

    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    page = 1
    start_no = 1
    all_data = []
    total_count = None

    MAX_PAGES = 300

    while page <= MAX_PAGES:

        log(f"[PAGE] {page}")

        data = parse_page(driver, page, start_no, today)

        if not data:
            break

        all_data.extend(data)

        start_no += len(data)
        page += 1

        # =========================
        # 総件数取得（初回のみ）
        # =========================
        if total_count is None:

            text = driver.find_element(By.TAG_NAME, "body").text
            total_count = get_total_count(text)

            log(f"[TOTAL] {total_count}")

        log(f"[COUNT] {len(all_data)}")

        if total_count and len(all_data) >= total_count:
            break

        time.sleep(0.5)

    driver.quit()

    # =========================
    # CSV出力
    # =========================
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        writer.writerow([
            "日付",
            "順位",
            "銘柄名",
            "コード",
            "市場",
            "株価",
            "前日差",
            "騰落率",
            "出来高",
            "PER",
            "PBR",
            "配当利回り"
        ])

        writer.writerows(all_data)

    end_time = datetime.datetime.now(JST)

    log("===== END =====")
    log(f"[FILE] {csv_file}")
    log(f"[ROWS] {len(all_data)}")


if __name__ == "__main__":
    main()
