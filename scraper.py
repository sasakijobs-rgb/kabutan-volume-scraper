import os
import time
import csv
from datetime import datetime
import glob
import pandas as pd
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# =========================
# 設定
# =========================
MAX_FILES = 150

FOLDER = os.path.join(os.getcwd(), "output")

# テスト用
TOTAL_PAGES = 2
TOP_N = 30

BASE_URL = (
    "https://kabutan.jp/warning/trading_value_ranking"
    "?market=0&capitalization=-1&dispmode=normal&stc=&stm=0"
)

os.makedirs(FOLDER, exist_ok=True)

# =========================
# ログ
# =========================
log_file = os.path.join(
    FOLDER,
    "trading_value_ranking.log"
)

def log(msg):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    text = f"{timestamp} {msg}"

    print(text)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# =========================
# 前回比較
# =========================
first_page_file = os.path.join(
    FOLDER,
    "first_page15_before.csv"
)

if os.path.exists(first_page_file):

    prev_head15 = open(
        first_page_file,
        "r",
        encoding="utf-8"
    ).read().splitlines()

    log(f"比較ファイル: {os.path.basename(first_page_file)}")

else:

    prev_head15 = []

    log("比較ファイル: なし")

# =========================
# 今日のCSV
# =========================
today = datetime.now().strftime("%Y%m%d")

filename = os.path.join(
    FOLDER,
    f"trading_value_ranking_{today}.csv"
)

# =========================
# Selenium設定
# =========================
options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

options.add_argument(
    "--user-agent=Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

driver = None

start_time = datetime.now()

rank = 1

first_page_rows_text = []

log("【売買代金ランキング取得 開始】")

try:

    log("Chrome 起動開始")

    driver = webdriver.Chrome(options=options)

    log("Chrome 起動完了")

    with open(filename, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "No",
            "コード",
            "銘柄名",
            "市場",
            "株価",
            "前日比",
            "前日比(%)",
            "売買代金",
            "PER(倍)",
            "PBR(倍)",
            "利回り(%)"
        ])

        for page_no in range(1, TOTAL_PAGES + 1):

            log(f"{page_no:03d}/{TOTAL_PAGES:03d}")

            url = f"{BASE_URL}&page={page_no}"

            log(f"URL: {url}")

            try:
                driver.set_page_load_timeout(30)
                driver.get(url)
            except Exception as e:
                log(f"ページ取得エラー: {e}")
                continue

            time.sleep(5)

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            log(f"取得行数: {len(rows)}")

            if not rows:
                log(driver.page_source[:3000])
                continue

            for i, row in enumerate(rows):

                try:

                    row_text = row.text.replace("\n", " ").strip()

                    log(f"row[{i}] = {row_text[:120]}")

                    if not row_text:
                        continue

                    if "日 中 足" in row_text:
                        continue

                    parts = row_text.split()

                    if len(parts) < 10:
                        continue

                    code = parts[0]
                    name = parts[1]
                    market = parts[2]

                    price = parts[3]
                    prev_diff = parts[4]
                    prev_diff_percent = parts[5].replace("%", "")

                    trading_value = parts[6].replace(",", "")

                    per = parts[7].replace("倍", "")
                    pbr = parts[8].replace("倍", "")
                    yield_ = parts[9].replace("%", "")

                    if page_no == 1 and i < 15:
                        first_page_rows_text.append(row_text)

                    if (
                        page_no == 1
                        and i < 15
                        and prev_head15
                        and i < len(prev_head15)
                    ):
                        if row_text == prev_head15[i]:
                            log("前回と同じデータのため終了")
                            sys.exit(0)

                    writer.writerow([
                        rank,
                        code,
                        name,
                        market,
                        price,
                        prev_diff,
                        prev_diff_percent,
                        trading_value,
                        per,
                        pbr,
                        yield_
                    ])

                    log(f"保存: {rank} {code} {name}")

                    rank += 1

                    if rank > TOP_N:
                        break

                except Exception as e:
                    log(f"行解析エラー: {e}")
                    continue

            if rank > TOP_N:
                break

except Exception as e:
    log(f"重大エラー: {e}")

finally:
    if driver:
        driver.quit()
        log("ブラウザ終了")

# =========================
# 比較ファイル保存
# =========================
try:
    with open(first_page_file, "w", encoding="utf-8") as f:
        for line in first_page_rows_text[:15]:
            f.write(line + "\n")
    log("比較ファイル保存完了")

except Exception as e:
    log(f"比較ファイル保存失敗: {e}")

# =========================
# ★ merged処理（テスト中は無効化）
# =========================

"""
all_files = sorted(
    glob.glob(os.path.join(FOLDER, "trading_value_ranking_*.csv"))
)

merge_files = [
    f for f in all_files
    if "merged" not in f
]

df_list = []

for csv_file in merge_files:

    try:
        df = pd.read_csv(csv_file, encoding="utf-8")
        df.insert(0, "日付", csv_file.split("_")[-1].replace(".csv", ""))
        df_list.append(df)

    except Exception as e:
        log(f"CSV読込失敗: {e}")

if df_list:

    df_all = pd.concat(df_list, ignore_index=True)

    merged_filename = os.path.join(
        FOLDER,
        "trading_value_ranking_merged.csv"
    )

    df_all.to_csv(
        merged_filename,
        index=False,
        encoding="utf-8"
    )

    log(f"結合完了: {merged_filename}")
"""

# =========================
# 終了
# =========================
end_time = datetime.now()

log(f"処理時間: {(end_time - start_time).seconds}秒")
