import os
import time
import random
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# 設定
# ==========================================
BASE_URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={}"

MAX_PAGES = 300

today = datetime.now().strftime("%Y%m%d")

os.makedirs("output", exist_ok=True)

merged_file = "output/trading_value_ranking_merged.csv"
daily_file = f"output/trading_value_ranking_{today}.csv"

header = [
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
]

# ==========================================
# merged 初回ヘッダー作成
# ==========================================
if not os.path.exists(merged_file):
    with open(merged_file, "w", newline="", encoding="utf-8-sig") as f:
        csv.writer(f).writerow(header)

# ==========================================
# 古いファイル削除（150制限）
# ==========================================
def cleanup_old_daily_files():
    folder = "output"
    prefix = "trading_value_ranking_"
    suffix = ".csv"

    files = []

    for f in os.listdir(folder):
        if f.startswith(prefix) and f.endswith(suffix):
            date_str = f.replace(prefix, "").replace(suffix, "")
            if date_str.isdigit():
                files.append((date_str, f))

    files.sort(key=lambda x: x[0])

    MAX_FILES = 150

    if len(files) > MAX_FILES:
        for _, filename in files[:len(files) - MAX_FILES]:
            try:
                os.remove(os.path.join(folder, filename))
                print(f"🗑 削除: {filename}")
            except Exception as e:
                print(f"⚠ 削除失敗: {filename} ({e})")

# ==========================================
# Chrome
# ==========================================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1400,2200")

driver = webdriver.Chrome(options=options)

# ==========================================
# メイン
# ==========================================
try:
    print("===== START =====")

    cleanup_old_daily_files()

    with open(daily_file, "w", newline="", encoding="utf-8-sig") as df, \
         open(merged_file, "a", newline="", encoding="utf-8-sig") as mf:

        daily_writer = csv.writer(df)
        merged_writer = csv.writer(mf)

        daily_writer.writerow(header)

        rank = 1
        empty_count = 0

        # ==========================================
        # ページループ（毎回実行）
        # ==========================================
        for page in range(1, MAX_PAGES + 1):

            url = BASE_URL.format(page)
            print("PAGE:", page, url)

            driver.get(url)
            time.sleep(random.uniform(2, 4))

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            if len(rows) == 0:
                empty_count += 1
                print(f"⚠ empty page {page} ({empty_count})")

                if empty_count >= 3:
                    print("⚠ 連続空ページ → 終了")
                    break
                continue

            empty_count = 0

            for row in rows:

                tds = row.find_elements(By.TAG_NAME, "td")

                if len(tds) < 8:
                    continue

                try:
                    code = tds[0].text.strip()

                    if not code.isdigit():
                        continue

                    name = tds[1].text.strip()
                    market = tds[2].text.strip()

                    price = tds[3].text.strip()
                    prev_value = tds[4].text.strip()
                    prev_rate = tds[5].text.strip()
                    trading_value = tds[6].text.strip()
                    per = tds[7].text.strip() if len(tds) > 7 else ""
                    pbr = tds[8].text.strip() if len(tds) > 8 else ""
                    yield_value = tds[9].text.strip() if len(tds) > 9 else ""

                    price = price.replace(",", "")
                    prev_value = prev_value.replace(",", "")
                    trading_value = trading_value.replace(",", "")

                    row_data = [
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
                    ]

                    daily_writer.writerow(row_data)
                    merged_writer.writerow(row_data)

                    rank += 1

                except Exception as e:
                    print("⚠ row error:", e)

    print("===== 完了 =====")
    print("daily:", daily_file)
    print("merged:", merged_file)

finally:
    driver.quit()
    print("===== END =====")
