import os
import time
import random
import csv
from datetime import datetime
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import sys

# =========================
# 設定
# =========================
MAX_FILES = 150
FOLDER = "output"
TOTAL_PAGES = 25
TOP_N = 3000
BASE_URL = "https://s.kabutan.jp/warnings/volume_ranking/?market=all"

os.makedirs(FOLDER, exist_ok=True)

# ログ関数
log_file = os.path.join(FOLDER, "volume_ranking.log")
def log(msg):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} {msg}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {msg}\n")

# =========================
# 前回比較ファイル
# =========================
first_page_file = os.path.join(FOLDER, "first_page20_before.csv")
if os.path.exists(first_page_file):
    prev_head20 = open(first_page_file, "r", encoding="utf-8").read().splitlines()
    log(f"比較ファイル: {os.path.basename(first_page_file)}")
else:
    prev_head20 = []
    log("比較ファイル: なし")

# =========================
# 今日のCSVファイル名
# =========================
today = datetime.now().strftime("%Y%m%d")
filename = os.path.join(FOLDER, f"volume_ranking_{today}.csv")

# =========================
# Seleniumセットアップ
# =========================
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64)")
driver = None

start_time = datetime.now()
rank = 1
log("【データ取得 開始】")

try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # CSVヘッダー作成
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow([
            "No","コード","銘柄名","市場","株価","前日比","前日比(%)",
            "出来高","PER","PBR","利回り","売買金額"
        ])

    first_page_rows_text = []

    for page_no in range(1, TOTAL_PAGES + 1):
        page_str = f"{page_no:03d}/{TOTAL_PAGES:03d}"
        log(page_str)
        url = BASE_URL if page_no == 1 else f"{BASE_URL}&page={page_no}"

        try:
            driver.get(url)
        except Exception as e:
            log(f"ページ取得エラー: {url} ({e})")
            continue

        time.sleep(2 + random.random())

        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")
        if not rows:
            log(f"データ取得警告: 行が見つかりません - {url}")
            continue

        for i, row in enumerate(rows):
            row_text = row.text.replace("\n", " ").strip()
            if page_no == 1 and i < 20:
                first_page_rows_text.append(row_text)

            if page_no == 1 and i < 20 and prev_head20:
                if row_text == prev_head20[i]:
                    log("前回と同じデータのため処理を中断します（正常終了）")
                    # 終了コード0で正常終了
                    sys.exit(0)

            try:
                # 銘柄名
                name_elem = row.find_elements(By.CSS_SELECTOR, "th a p, th a abbr")
                if not name_elem:
                    continue
                name = name_elem[0].text.strip()

                # 株コード・市場
                code_market_div = row.find_elements(By.CSS_SELECTOR, "th a div.flex")
                code, market = "", ""
                if code_market_div:
                    parts = code_market_div[0].text.split()
                    code = parts[0].strip() if len(parts) >= 1 else ""
                    market = parts[1].strip() if len(parts) >= 2 else ""

                tds = row.find_elements(By.TAG_NAME, "td")
                if len(tds) < 7:
                    continue

                price = tds[0].text.strip()
                prev_text = tds[1].text.split("\n")
                prev_diff = prev_text[0].strip()
                prev_diff_percent = prev_text[1].replace("%","").strip() if len(prev_text) > 1 else ""
                volume = tds[2].text.strip()
                per = tds[4].text.strip()
                pbr = tds[5].text.strip()
                yield_ = tds[6].text.strip()

                # 売買金額計算
                try:
                    price_num = float(price.replace(",",""))
                    volume_num = float(volume.replace(",","").replace("株",""))
                    trade_amount = int(price_num * volume_num)
                except:
                    trade_amount = 0

                record = [
                    rank, code, name, market, price, prev_diff, prev_diff_percent,
                    volume, per, pbr, yield_, trade_amount
                ]

                with open(filename, "a", newline="", encoding="utf-8-sig") as f:
                    writer = csv.writer(f)
                    writer.writerow(record)

                rank += 1
                if rank > TOP_N:
                    break

            except Exception as e:
                log(f"データ取得エラー: {e}")
                continue  # 続行

        if rank > TOP_N:
            break

except Exception as e:
    log(f"処理中断例外: {e}")

finally:
    if driver:
        driver.quit()
        log("ブラウザ終了")

# =========================
# first_page20_before.csv 保存（取得データ1ページ目）
# =========================
with open(first_page_file, "w", encoding="utf-8") as f:
    for line in first_page_rows_text[:20]:
        f.write(line + "\n")

# =========================
# 処理終了ログ
# =========================
end_time = datetime.now()
delta_sec = int((end_time - start_time).total_seconds())
log(f"【データ取得 終了】 (処理時間：{delta_sec}秒)")

# =========================
# 古いCSV削除
# =========================
all_files = sorted(glob.glob(os.path.join(FOLDER, "volume_ranking_*.csv")))
if len(all_files) > MAX_FILES:
    for f in all_files[:-MAX_FILES]:
        try:
            os.remove(f)
        except Exception as e:
            log(f"削除失敗: {f} ({e})")

# =========================
# マージファイル作成
# =========================
merge_files = [f for f in sorted(glob.glob(os.path.join(FOLDER, "volume_ranking_*.csv")))
               if "merged" not in f and "first_page20_before.csv" not in f]

df_list = []
for f in merge_files:
    df = pd.read_csv(f, encoding="utf-8-sig")
    df.insert(0, "日付", f.split("_")[-1].replace(".csv",""))
    df_list.append(df)

if df_list:
    df_all = pd.concat(df_list, ignore_index=True)
    merged_filename = os.path.join(FOLDER, "volume_ranking_merged.csv")
    df_all.to_csv(merged_filename, index=False, encoding="utf-8-sig")
    log(f"結合完了: {merged_filename}")