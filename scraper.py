import os
import csv
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# =========================
# 設定
# =========================
FOLDER = "output"
os.makedirs(FOLDER, exist_ok=True)

TOTAL_PAGES = 2
TOP_N = 30

BASE_URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&stc=&stm=0&page="

today = datetime.now().strftime("%Y%m%d")
csv_path = os.path.join(FOLDER, f"trading_value_ranking_{today}.csv")

log_file = os.path.join(FOLDER, "log.txt")

def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{t} {msg}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{t} {msg}\n")

headers = {
    "User-Agent": "Mozilla/5.0"
}

log("開始")

rank = 1

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "No","コード","銘柄名","市場","株価",
        "前日比","前日比(%)","売買代金",
        "PER","PBR","利回り"
    ])

    for page in range(1, TOTAL_PAGES + 1):

        url = BASE_URL + str(page)
        log(url)

        res = requests.get(url, headers=headers, timeout=20)

        if res.status_code != 200:
            log(f"HTTPエラー {res.status_code}")
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        # ★ここが正解ポイント
        table = soup.select_one("table.stock_table.st_market")

        if not table:
            log("tableなし")
            continue

        rows = table.select("tbody tr")

        log(f"rows: {len(rows)}")

        for row in rows:

            th = row.find("th")
            tds = row.find_all("td")

            if not th or len(tds) < 8:
                continue

            try:
                # コード + 銘柄名
                code = th.find("a").text.strip()
                name = th.text.replace(code, "").strip()

                market = tds[0].text.strip()
                price = tds[2].text.strip()

                diff = tds[4].text.strip()
                diff_pct = tds[5].text.replace("%", "").strip()

                trading_value = tds[6].text.replace(",", "").strip()

                per = tds[7].text.strip().replace("倍", "")
                pbr = tds[8].text.strip().replace("倍", "")
                yield_ = tds[9].text.strip().replace("%", "")

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

                rank += 1

                if rank > TOP_N:
                    break

            except Exception:
                continue

        if rank > TOP_N:
            break

log("完了")
