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
# merged 初回作成
# ==========================================
if not os.path.exists(merged_file):
    with open(merged_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)

# ==========================================
# 古い日次CSV削除（150件保持）
# ==========================================
def cleanup_old_daily_files():

    folder = "output"
    prefix = "trading_value_ranking_"
    suffix = ".csv"

    files = []

    for f in os.listdir(folder):

        if not f.startswith(prefix):
            continue

        if not f.endswith(suffix):
            continue

        # merged除外
        if "merged" in f:
            continue

        date_str = f.replace(prefix, "").replace(suffix, "")

        if not date_str.isdigit():
            continue

        files.append((date_str, f))

    # 古い順
    files.sort(key=lambda x: x[0])

    MAX_FILES = 150

    if len(files) > MAX_FILES:

        delete_targets = files[:len(files) - MAX_FILES]

        for _, filename in delete_targets:

            path = os.path.join(folder, filename)

            try:
                os.remove(path)
                print("🗑 削除:", filename)

            except Exception as e:
                print("⚠ 削除失敗:", filename, e)

# ==========================================
# Chrome
# ==========================================
options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1400,2200")

options.add_argument(
    "--user-agent=Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

# ==========================================
# メイン
# ==========================================
try:

    print("===== START =====")

    cleanup_old_daily_files()

    # ==========================================
    # CSV作成
    # ==========================================
    with open(daily_file, "w", newline="", encoding="utf-8-sig") as df, \
         open(merged_file, "a", newline="", encoding="utf-8-sig") as mf:

        daily_writer = csv.writer(df)
        merged_writer = csv.writer(mf)

        # dailyのみ見出し
        daily_writer.writerow(header)

        rank = 1
        empty_count = 0

        # ==========================================
        # ページ取得
        # ==========================================
        for page in range(1, MAX_PAGES + 1):

            url = BASE_URL.format(page)

            print("\nPAGE:", page)
            print(url)

            driver.get(url)

            time.sleep(random.uniform(2, 4))

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            print("rows:", len(rows))

            # 空ページ検知
            if len(rows) == 0:

                empty_count += 1

                print(f"⚠ empty page ({empty_count})")

                if empty_count >= 3:
                    print("⚠ 3連続空ページ → 終了")
                    break

                continue

            empty_count = 0

            page_valid_count = 0

            # ==========================================
            # 行解析
            # ==========================================
            for row in rows:

                try:

                    # td + th 両対応
                    cells = row.find_elements(
                        By.CSS_SELECTOR,
                        "td, th"
                    )

                    # デバッグ
                    print("cells:", len(cells))

                    if len(cells) < 8:
                        continue

                    values = []

                    for c in cells:
                        txt = c.text.strip()
                        values.append(txt)

                    # デバッグ
                    print(values)

                    code = values[0]

                    # 数字コード以外除外
                    if not code.isdigit():
                        continue

                    name = values[1]
                    market = values[2]

                    price = values[3]
                    prev_value = values[4]
                    prev_rate = values[5]
                    trading_value = values[6]

                    per = values[7] if len(values) > 7 else ""
                    pbr = values[8] if len(values) > 8 else ""
                    yield_value = values[9] if len(values) > 9 else ""

                    # カンマ除去
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

                    page_valid_count += 1

                    print("✔", rank, code, name)

                    rank += 1

                except Exception as e:

                    print("⚠ row error:", e)

                    try:
                        print(row.get_attribute("innerHTML"))
                    except:
                        pass

                    continue

            print("valid rows:", page_valid_count)

    print("\n===== 完了 =====")
    print("daily :", daily_file)
    print("merged:", merged_file)

finally:

    driver.quit()

    print("===== END =====")
