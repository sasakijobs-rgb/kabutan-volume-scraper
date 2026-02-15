import os
import glob
import time
import random
import requests
import csv
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

# =========================
# 設定
# =========================
MAX_FILES = 150
FOLDER = "/home/yourusername/output"  # 保存先
TOTAL_PAGES = 200  # 1ページ15件 × 200ページ = 3000件
TOP_N = 3000       # 最大取得件数
BASE_URL = "https://kabutan.jp/warning/volume_ranking"
HEADERS = {"User-Agent": "Mozilla/5.0"}

# =========================
# 開始表示
# =========================
start_time = time.time()
print("===================================")
print("出来高ランキング取得開始")
print("===================================")

# =========================
# フォルダ作成
# =========================
os.makedirs(FOLDER, exist_ok=True)

# =========================
# 今日のファイル名
# =========================
today = datetime.now().strftime("%Y%m%d")
filename = os.path.join(FOLDER, f"volume_ranking_{today}.csv")
print(f"保存先: {filename}\n")

# =========================
# データ取得
# =========================
all_data = []
rank = 1

for page_no in range(1, TOTAL_PAGES + 1):
    url = BASE_URL if page_no == 1 else f"{BASE_URL}?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={page_no}"
    print(f"[{page_no}/{TOTAL_PAGES}] ページ取得中...")
    print(f"URL: {url}")

    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="stock_table")

    if table is None:
        print("⚠ テーブルが見つかりませんでした")
        continue

    rows = table.find("tbody").find_all("tr")
    print(f"→ {len(rows)}件見つかりました")

    for row in rows:
        cols = row.find_all(["td", "th"])
        data = [col.get_text(strip=True) for col in cols]

        if len(data) < 13:
            continue

        record = [
            rank,
            data[0],  # コード
            data[1],  # 銘柄名
            data[2],  # 市場
            data[5],  # 株価
            data[7],  # 前日比
            data[8],  # 前日比(%)
            data[9],  # 出来高
            data[10], # PER
            data[11], # PBR
            data[12], # 利回り
        ]

        all_data.append(record)
        rank += 1

        if len(all_data) >= TOP_N:  # 3000件取得で停止
            break
    if len(all_data) >= TOP_N:
        print(f"取得件数 {TOP_N} に到達しました。終了します。")
        break

    # ランダム待機（スクレイピング負荷軽減）
    wait_time = random.uniform(1, 3)
    print(f"待機中... {wait_time:.2f}秒\n")
    time.sleep(wait_time)

print(f"合計取得件数: {len(all_data)}件\n")

# =========================
# CSV保存
# =========================
print("CSV保存中...")
with open(filename, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow([
        "No", "コード", "銘柄名", "市場", "株価", "前日比",
        "前日比(%)", "出来高", "PER", "PBR", "利回り"
    ])
    writer.writerows(all_data)

print("保存完了\n")

# =========================
# 直近150ファイルのみ保持
# =========================
print("古いファイル整理中...")
files = sorted(glob.glob(os.path.join(FOLDER, "volume_ranking_*.csv")))
deleted_count = 0
if len(files) > MAX_FILES:
    files_to_delete = files[:-MAX_FILES]
    for file in files_to_delete:
        os.remove(file)
        deleted_count += 1

print(f"削除ファイル数: {deleted_count}")
print(f"現在の保存ファイル数: {min(len(files), MAX_FILES)}")

# =========================
# CSVを1つにまとめる
# =========================
print("CSVを1つにまとめ中...")
all_files = sorted(glob.glob(os.path.join(FOLDER, "volume_ranking_*.csv")))
df_list = [pd.read_csv(f, encoding="utf-8-sig") for f in all_files]
if df_list:
    combined_df = pd.concat(df_list, ignore_index=True)
    combined_file = os.path.join(FOLDER, "volume_ranking_all.csv")
    combined_df.to_csv(combined_file, index=False, encoding="utf-8-sig")
    print(f"統合CSV保存: {combined_file}")

# =========================
# 終了表示
# =========================
elapsed = time.time() - start_time
print("\n===================================")
print("処理完了")
print(f"実行時間: {elapsed:.2f}秒")
print("===================================")
