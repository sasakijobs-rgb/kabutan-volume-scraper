import os
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# =========================
# 設定
# =========================
FOLDER = os.path.join(os.getcwd(), "output")
os.makedirs(FOLDER, exist_ok=True)

TOTAL_PAGES = 2   # テスト
TOP_N = 30

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

        rows = soup.select("table.stock_table tr")

        log(f"取得行数: {len(rows)}")

        for row in rows:

            cols = row.find_all("td")

            if len(cols) < 10:
                continue

            try:
                code_name = row.find("th").get_text(strip=True)

                if not code_name:
                    continue

                code = code_name.split()[0]
                name = code_name.split()[1]

                market = cols[0].get_text(strip=True)
                price = cols[1].get_text(strip=True)

                diff = cols[2].get_text(strip=True)
                diff_pct = cols[3].get_text(strip=True).replace("%", "")

                trading_value = cols[4].get_text(strip=True).replace(",", "")

                per = cols[5].get_text(strip=True).replace("倍", "")
                pbr = cols[6].get_text(strip=True).replace("倍", "")
                yield_ = cols[7].get_text(strip=True).replace("%", "")

                writer.writerow([
                    rank,
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
                ])

                log(f"保存 {rank} {code} {name}")

                rank += 1

                if rank > TOP_N:
                    break

            except Exception:
                continue

        if rank > TOP_N:
            break

log("完了")
