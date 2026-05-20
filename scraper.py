import os
import time
import random
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# URL
# ==========================================
BASE_URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page={}"

print("===== START =====")

today = datetime.now().strftime("%Y%m%d")

os.makedirs("output", exist_ok=True)

output_csv = f"output/trading_value_ranking_{today}.csv"
first_page_file = "output/first_page15_before.csv"

# ==========================================
# Chrome
# ==========================================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--window-size=1400,2200")

options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

options.binary_location = "/usr/bin/chromium-browser"

driver = webdriver.Chrome(options=options)

try:

    # ==========================================
    # 1ページ目取得（比較用）
    # ==========================================
    print("\n===== PAGE 1 CHECK =====")
    driver.get(BASE_URL.format(1))
    time.sleep(random.uniform(5, 8))

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    current_page_snapshot = []
    for r in rows[:15]:
        txt = r.text.strip().replace("\n", " | ")
        current_page_snapshot.append(txt)

    current_snapshot_str = "\n".join(current_page_snapshot)

    # ==========================================
    # 前回データ読み込み
    # ==========================================
    if os.path.exists(first_page_file):
        with open(first_page_file, "r", encoding="utf-8") as f:
            prev_snapshot_str = f.read().strip()
    else:
        prev_snapshot_str = ""

    # ==========================================
    # 比較
    # ==========================================
    if current_snapshot_str == prev_snapshot_str:
        print("\n⚠ 1ページ目が前回と完全一致 → 処理終了")
        driver.quit()
        exit()

    print("\n✔ データ更新あり → 続行")

    # ==========================================
    # 新データ保存（生データ）
    # ==========================================
    with open(first_page_file, "w", encoding="utf-8") as f:
        f.write(current_snapshot_str)

    # ==========================================
    # 本処理CSV
    # ==========================================
    with open(output_csv, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        writer.writerow([
            "日付",
            "順位",
            "コード",
            "銘柄名",
            "市場",
            "株価(百万円)",
            "前日比(値)",
            "前日比(率)",
            "売買代金",
            "PER",
            "PBR",
            "利回り"
        ])

        rank = 1

        # ==========================================
        # 2ページ取得
        # ==========================================
        for page in range(1, 3):

            url = BASE_URL.format(page)
            print("\nPAGE:", page, url)

            driver.get(url)
            time.sleep(random.uniform(5, 8))

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            for row in rows:

                lines = row.text.split("\n")
                if len(lines) < 5:
                    continue

                name = lines[0].strip()
                code = lines[1].strip()
                market = lines[2].strip()

                price_prev = lines[3].strip()
                remain = lines[4].strip()

                # 株価分離
                import re
                m = re.match(r"(.+?)\s+([+-].+)", price_prev)

                if m:
                    price = m.group(1)
                    prev_value = m.group(2)
                else:
                    price = price_prev
                    prev_value = ""

                parts = remain.split()

                prev_rate = parts[0] if len(parts) > 0 else ""
                trading_value = parts[1] if len(parts) > 1 else ""
                per = parts[2] if len(parts) > 2 else ""
                pbr = parts[3] if len(parts) > 3 else ""
                yield_value = parts[4] if len(parts) > 4 else ""

                # カンマ除去
                price = price.replace(",", "")
                prev_value = prev_value.replace(",", "")
                trading_value = trading_value.replace(",", "")

                writer.writerow([
                    today,
                    rank,
                    code,
                    name,
                    market,
                    price,
                    prev_value,
                    prev_rate,
                    trading_value,
                    per,
                    pbr,
                    yield_value
                ])

                rank += 1

                if rank > 30:
                    break

            if rank > 30:
                break

    driver.save_screenshot("debug.png")

    print("\n===== 完了 =====")
    print("CSV:", output_csv)

finally:
    driver.quit()
    print("===== END =====")
