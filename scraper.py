import os
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import glob
import pandas as pd

# =========================
# 設定
# =========================
FOLDER = os.path.join(os.getcwd(), "output")
os.makedirs(FOLDER, exist_ok=True)

TOTAL_PAGES = 200
TOP_N = 3000

BASE_URL = (
    "https://kabutan.jp/warning/trading_value_ranking"
    "?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page="
)

today = datetime.now().strftime("%Y%m%d")

filename = os.path.join(
    FOLDER,
    f"trading_value_ranking_{today}.csv"
)

log_file = os.path.join(FOLDER, "trading_value_ranking.log")

# =========================
# ログ
# =========================
def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    text = f"{t} {msg}"
    print(text)
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(text + "\n")

# =========================
# ヘッダ
# =========================
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# =========================
# 解析関数（重要）
# =========================
def parse_row(row):

    th = row.find("th")
    tds = row.find_all("td")

    if not th or len(tds) < 7:
        return None

    try:
        # 銘柄（コード + 名前）
        th_text = th.get_text(" ", strip=True)
        parts = th_text.split()

        if len(parts) < 2:
            return None

        code = parts[0]
        name = parts[1]

        market = tds[0].get_text(strip=True)
        price = tds[1].get_text(strip=True)

        diff = tds[2].get_text(strip=True)
        diff_pct = tds[3].get_text(strip=True).replace("%", "")

        trading_value = tds[4].get_text(strip=True).replace(",", "")

        per = tds[5].get_text(strip=True).replace("倍", "")
        pbr = tds[6].get_text(strip=True).replace("倍", "")
        yield_ = tds[7].get_text(strip=True).replace("%", "")

        return [
            code,
            name,
            market,
            price,
            diff,
            diff_pct,
            trading_value,
            per,
            pbr,
            yield_
        ]

    except Exception:
        return None

# =========================
# 開始
# =========================
log("【開始】")

rank = 1

with open(filename, "w", newline="", encoding="utf-8") as f:

    writer = csv.writer(f)

    writer.writerow([
        "No","コード","銘柄名","市場","株価",
        "前日比","前日比(%)","売買代金",
        "PER","PBR","利回り"
    ])

    for page in range(1, TOTAL_PAGES + 1):

        url = BASE_URL + str(page)
        log(url)

        try:
            res = requests.get(url, headers=headers, timeout=20)
        except Exception as e:
            log(f"リクエスト失敗: {e}")
            continue

        if res.status_code != 200:
            log(f"HTTPエラー: {res.status_code}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        rows = soup.find_all("tr")

        log(f"tr数: {len(rows)}")

        for row in rows:

            data = parse_row(row)

            if not data:
                continue

            writer.writerow([rank] + data)

            log(f"保存 {rank} {data[0]} {data[1]}")

            rank += 1

            if rank > TOP_N:
                break

        if rank > TOP_N:
            break

log("データ取得完了")

# =========================
# merged（本番復活）
# =========================
log("merged作成開始")

files = sorted(
    glob.glob(os.path.join(FOLDER, "trading_value_ranking_*.csv"))
)

df_list = []

for file in files:

    try:
        df = pd.read_csv(file, encoding="utf-8")
        df.insert(
            0,
            "日付",
            file.split("_")[-1].replace(".csv", "")
        )
        df_list.append(df)

    except Exception as e:
        log(f"読込失敗: {file} {e}")

if df_list:

    df_all = pd.concat(df_list, ignore_index=True)

    merged_file = os.path.join(
        FOLDER,
        "trading_value_ranking_merged.csv"
    )

    df_all.to_csv(
        merged_file,
        index=False,
        encoding="utf-8"
    )

    log(f"merged完了: {merged_file}")

log("完了")
