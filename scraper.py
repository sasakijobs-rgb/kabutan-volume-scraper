import os
import time
import random
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
# ログ関数
# =========================
log_file = os.path.join(
    FOLDER,
    "trading_value_ranking.log"
)

def log(msg):

    timestamp = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    text = f"{timestamp} {msg}"

    print(text)

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# =========================
# 前回比較ファイル
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

# GitHub Actions対応
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

    # =========================
    # Chrome起動
    # =========================
    log("Chrome 起動開始")

    driver = webdriver.Chrome(options=options)

    log("Chrome 起動完了")

    # =========================
    # CSV作成
    # =========================
    with open(
        filename,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

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

        # =========================
        # ページ巡回
        # =========================
        for page_no in range(1, TOTAL_PAGES + 1):

            log(f"{page_no:03d}/{TOTAL_PAGES:03d}")

            url = f"{BASE_URL}&page={page_no}"

            log(f"URL: {url}")

            try:

                driver.get(url)

            except Exception as e:

                log(f"ページ取得エラー: {e}")

                continue

            # 読み込み待機
            time.sleep(5)

            # =========================
            # 行取得
            # =========================
            rows = driver.find_elements(
                By.CSS_SELECTOR,
                "tbody tr"
            )

            log(f"取得行数: {len(rows)}")

            # HTML確認
            if not rows:

                log("HTML先頭確認")

                html_preview = driver.page_source[:3000]

                log(html_preview)

                continue

            # =========================
            # 行解析
            # =========================
            for i, row in enumerate(rows):

                try:

                    row_text = (
                        row.text
                        .replace("\n", " ")
                        .strip()
                    )

                    log(f"row[{i}] = {row_text[:120]}")

                    # =========================
                    # 比較保存
                    # =========================
                    if page_no == 1 and i < 15:

                        first_page_rows_text.append(
                            row_text
                        )

                    # =========================
                    # 前回比較
                    # =========================
                    if (
                        page_no == 1
                        and i < 15
                        and prev_head15
                        and i < len(prev_head15)
                    ):

                        if row_text == prev_head15[i]:

                            log(
                                "前回と同じデータのため終了"
                            )

                            sys.exit(0)

                    # =========================
                    # 銘柄名
                    # =========================
                    name_elem = row.find_elements(
                        By.CSS_SELECTOR,
                        "th a p, th a abbr"
                    )

                    if not name_elem:

                        log("銘柄名取得失敗")

                        continue

                    name = (
                        name_elem[0]
                        .text
                        .strip()
                    )

                    # =========================
                    # コード・市場
                    # =========================
                    code = ""
                    market = ""

                    code_market = row.find_elements(
                        By.CSS_SELECTOR,
                        "th a div.flex"
                    )

                    if code_market:

                        parts = (
                            code_market[0]
                            .text
                            .split()
                        )

                        if len(parts) >= 1:
                            code = parts[0].strip()

                        if len(parts) >= 2:
                            market = parts[1].strip()

                    # =========================
                    # td取得
                    # =========================
                    tds = row.find_elements(
                        By.TAG_NAME,
                        "td"
                    )

                    log(f"td数: {len(tds)}")

                    if len(tds) < 7:

                        log("td不足")

                        continue

                    # =========================
                    # データ取得
                    # =========================
                    price = tds[0].text.strip()

                    prev_text = (
                        tds[1]
                        .text
                        .split("\n")
                    )

                    prev_diff = (
                        prev_text[0].strip()
                        if len(prev_text) > 0
                        else ""
                    )

                    prev_diff_percent = (
                        prev_text[1]
                        .replace("%", "")
                        .strip()
                        if len(prev_text) > 1
                        else ""
                    )

                    trading_value = (
                        tds[2]
                        .text
                        .replace(",", "")
                        .replace("百万円", "")
                        .strip()
                    )

                    per = (
                        tds[4]
                        .text
                        .replace("倍", "")
                        .strip()
                    )

                    pbr = (
                        tds[5]
                        .text
                        .replace("倍", "")
                        .strip()
                    )

                    yield_ = (
                        tds[6]
                        .text
                        .replace("%", "")
                        .strip()
                    )

                    # =========================
                    # CSV保存
                    # =========================
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

                    log(
                        f"保存: {rank} {code} {name}"
                    )

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

    with open(
        first_page_file,
        "w",
        encoding="utf-8"
    ) as f:

        for line in first_page_rows_text[:15]:

            f.write(line + "\n")

    log("比較ファイル保存完了")

except Exception as e:

    log(f"比較ファイル保存失敗: {e}")

# =========================
# 古いCSV削除
# =========================
all_files = sorted(
    glob.glob(
        os.path.join(
            FOLDER,
            "trading_value_ranking_*.csv"
        )
    )
)

if len(all_files) > MAX_FILES:

    for old_file in all_files[:-MAX_FILES]:

        try:

            os.remove(old_file)

        except Exception as e:

            log(f"削除失敗: {e}")

# =========================
# merged作成
# =========================
merge_files = [
    f for f in sorted(
        glob.glob(
            os.path.join(
                FOLDER,
                "trading_value_ranking_*.csv"
            )
        )
    )
    if "merged" not in f
]

df_list = []

for csv_file in merge_files:

    try:

        df = pd.read_csv(
            csv_file,
            encoding="utf-8"
        )

        df.insert(
            0,
            "日付",
            csv_file.split("_")[-1]
            .replace(".csv", "")
        )

        df_list.append(df)

    except Exception as e:

        log(f"CSV読込失敗: {e}")

if df_list:

    try:

        df_all = pd.concat(
            df_list,
            ignore_index=True
        )

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

    except Exception as e:

        log(f"merged作成失敗: {e}")

# =========================
# 終了ログ
# =========================
end_time = datetime.now()

log(
    f"処理時間: {(end_time - start_time).seconds}秒"
)
