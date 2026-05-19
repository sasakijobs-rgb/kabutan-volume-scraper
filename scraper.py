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

TOTAL_PAGES = 2  # ★切り分け用
TOP_N = 30

BASE_URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&stc=&stm=0&page="

today = datetime.now().strftime("%Y%m%d")
csv_path = os.path.join(FOLDER, f"trading_value_ranking_{today}.csv")

log_file = os.path.join(FOLDER, "log.txt")

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
        "Chrome/124.0 Safari/537.36"
    ),
    "Referer": "https://kabutan.jp/",
    "Accept-Language": "ja-JP,ja;q=0.9"
}

log("開始（デバッグモード）")

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
        log(f"URL: {url}")

        res = requests.get(url, headers=headers, timeout=20)

        log(f"HTTP: {res.status_code}")

        if res.status_code != 200:
            log(res.text[:300])
            continue

        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.select_one("table.stock_table.st_market")

        if not table:
            log("tableなし")
            log(res.text[:500])
            continue

        rows = table.select("tbody tr")

        log(f"rows: {len(rows)}")

        # =========================
        # ★デバッグ核心部分
        # =========================
        for i, row in enumerate(rows):

            raw = row.get_text(" | ", strip=True)
            log(f"ROW[{i}] {raw}")

            # ★ここで一旦停止（パースしない）
            continue

log("完了")
