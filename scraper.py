import os
import time
import csv
from datetime import datetime
import glob
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# =========================
# 設定
# =========================
FOLDER = os.path.join(os.getcwd(), "output")

TOTAL_PAGES = 2   # テスト
TOP_N = 30

BASE_URL = (
    "https://kabutan.jp/warning/trading_value_ranking"
    "?market=0&capitalization=-1&dispmode=normal&stc=&stm=0"
)

os.makedirs(FOLDER, exist_ok=True)

# =========================
# ログ
# =========================
log_file = os.path.join(FOLDER, "trading_value_ranking.log")

def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"{t} {msg}"
    print(text)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# =========================
# 前回比較
# =========================
first_page_file = os.path.join(FOLDER, "first_page15_before.csv")

if os.path.exists(first_page_file):
    prev_head15 = open(first_page_file, "r", encoding="utf-8").read().splitlines()
    log(f"比較ファイル: {os.path.basename(first_page_file)}")
else:
    prev_head15 = []
    log("比較ファイル: なし")

# =========================
# CSV
# =========================
today = datetime.now().strftime("%Y%m%d")

filename = os.path.join(
    FOLDER,
    f"trading_value_ranking_{today}.csv"
)

# =========================
# Selenium設定（安定版）
# =========================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

driver = None

rank = 1
first_page_rows_text = []

log("【開始】")

try:

    log("Chrome 起動")

    driver = webdriver.Chrome(options=options)

    log("Chrome 起動完了")

    with open(filename, "w", newline="", encoding="utf-8") as f:

        writer = csv.writer(f)

        writer.writerow([
            "No","コード","銘柄名","市場","株価",
            "前日比","前日比(%)","売買代金",
            "PER","PBR","利回り"
        ])

        for page_no in range(1, TOTAL_PAGES + 1):

            log(f"{page_no}/{TOTAL_PAGES}")

            url = f"{BASE_URL}&page={page_no}"
            log(url)

            # =========================
            # timeout対策
            # =========================
            driver.set_page_load_timeout(60)

            try:
                driver.get(url)
            except Exception:
                log("timeout発生 → window.stop()")
                driver.execute_script("window.stop();")

            time.sleep(4)

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            log(f"取得行数: {len(rows)}")

            if not rows:
                log(driver.page_source[:1000])
                continue

            for i, row in enumerate(rows):

                try:
                    row_text = row.text.replace("\n", " ").strip()

                    if not row_text:
                        continue

                    parts = row_text.split()

                    # =========================
                    # ゴミ行除外（重要）
                    # =========================
                    if len(parts) < 11:
                        continue

                    if not parts[0].isdigit():
                        continue

                    # =========================
                    # 分解
                    # =========================
                    code = parts[0]
                    name = parts[1]
                    market = parts[2]

                    price = parts[3]
                    prev_diff = parts[4]

                    prev_diff_percent = parts[5].replace("%", "")

                    trading_value = parts[6].replace(",", "")

                    per = parts[7]
                    pbr = parts[8]
                    yield_ = parts[9]

                    # =========================
                    # 保存
                    # =========================
                    if page_no == 1 and i < 15:
                        first_page_rows_text.append(row_text)

                    if (
                        page_no == 1
                        and i < 15
                        and prev_head15
                        and i < len(prev_head15)
                    ):
                        if row_text == prev_head15[i]:
                            log("同一データ → 終了")
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

                    log(f"保存 {rank} {code} {name}")

                    rank += 1

                    if rank > TOP_N:
                        break

                except Exception as e:
                    log(f"行エラー: {e}")
                    continue

            if rank > TOP_N:
                break

except Exception as e:
    log(f"重大エラー: {e}")

finally:
    if driver:
        driver.quit()
        log("終了")

# =========================
# 比較保存
# =========================
try:
    with open(first_page_file, "w", encoding="utf-8") as f:
        for line in first_page_rows_text[:15]:
            f.write(line + "\n")
    log("比較保存OK")

except Exception as e:
    log(f"比較保存失敗: {e}")

# =========================
# ★ merged（テスト中は完全OFF）
# =========================
"""
merged処理は無効化（テスト高速化のため）
"""

# =========================
# 終了
# =========================
log("完了")
