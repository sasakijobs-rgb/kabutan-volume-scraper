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
FOLDER = "output"   # GitHub用
TOTAL_PAGES = 200
TOP_N = 3000
BASE_URL = "https://kabutan.jp/warning/volume_ranking"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# =========================
# 開始表示
# =========================
start_time = time.time()

print("===================================")
print("Kabutan 出来高ランキング取得開始")
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

print(f"保存先: {filename}")
print()

# =========================
# セッション
# =========================
session = requests.Session()
session.headers.update(HEADERS)

# =========================
# データ取得
# =========================
all_data = []
rank = 1

for page_no in range(1, TOTAL_PAGES + 1):

    if page_no == 1:
        url = BASE_URL
    else:
        url = f"{BASE_URL}?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={page_no}"

    print(f"[{page_no}/{TOTAL_PAGES}] ページ取得中")
    print(url)

    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print("取得失敗:", e)
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.find("table", class_="stock_table")

    if table is None:
        print("テーブルが見つかりません")
        continue

    tbody = table.find("tbody")

    if tbody is None:
        print("tbodyが見つかりません")
        continue

    rows = tbody.find_all("tr")

    print(f"{len(rows)}件取得")

    for row in rows:

        cols = row.find_all("td")

        data = [col.get_text(strip=True) for col in cols]

        if len(data) < 13:
            continue

        record = [
            rank,
            data[0],   # コード
            data[1],   # 銘柄名
            data[2],   # 市場
            data[5],   # 株価
            data[7],   # 前日比
            data[8],   # 前日比%
            data[9],   # 出来高
            data[10],  # PER
            data[11],  # PBR
            data[12],  # 利回り
        ]

        all_data.append(record)

        rank += 1

        if len(all_data) >= TOP_N:
            break

    if len(all_data) >= TOP_N:
        print("3000件取得完了")
        break

    wait = random.uniform(1, 2)
    print(f"待機 {wait:.2f}秒\n")
    time.sleep(wait)

print("取得件数:", len(all_data))
print()

# =========================
# CSV保存
# =========================
print("CSV保存中")

with open(filename, "w", newline="", encoding="utf-8-sig") as f:

    writer = csv.writer(f)

    writer.writerow([
        "No",
        "コード",
        "銘柄名",
        "市場",
        "株価",
        "前日比",
        "前日比(%)",
        "出来高",
        "PER",
        "PBR",
        "利回り"
    ])

    writer.writerows(all_data)

print("保存完了\n")

# =========================
# 古いファイル削除
# =========================
print("古いファイル整理")

files = sorted(glob.glob(os.path.join(FOLDER, "volume_ranking_*.csv")))

if len(files) > MAX_FILES:

    remove_files = files[:-MAX_FILES]

    for f in remove_files:
        os.remove(f)

    print(f"{len(remove_files)}ファイル削除")

else:
    print("削除なし")

print()

# =========================
# CSV統合
# =========================
print("CSV統合中")

all_files = sorted(glob.glob(os.path.join(FOLDER, "volume_ranking_*.csv")))

df_list = []

for f in all_files:

    try:
        df = pd.read_csv(f, encoding="utf-8-sig")
        df_list.append(df)
    except:
        pass

if df_list:

    combined = pd.concat(df_list, ignore_index=True)

    combined_file = os.path.join(FOLDER, "volume_ranking_all.csv")

    combined.to_csv(combined_file, index=False, encoding="utf-8-sig")

    print("統合CSV保存:", combined_file)

# =========================
# 終了
# =========================
elapsed = time.time() - start_time

print()
print("===================================")
print("処理完了")
print(f"実行時間: {elapsed:.2f}秒")
print("===================================")