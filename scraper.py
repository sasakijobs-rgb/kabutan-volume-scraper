import requests
from bs4 import BeautifulSoup
import csv
import os

url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&stc=&stm=0&page=1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers, timeout=20)

print("status:", res.status_code)

soup = BeautifulSoup(res.text, "html.parser")

table = soup.select_one("table.stock_table.st_market")

print("table found:", bool(table))

rows = table.select("tbody tr") if table else []

print("rows:", len(rows))

os.makedirs("output", exist_ok=True)
csv_path = "output/ranking_20260519.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)

    # ★あなたのヘッダーそのまま
    w.writerow([
        "No","コード","銘柄名","市場","株価",
        "前日比","前日比(%)","売買代金",
        "PER","PBR","利回り"
    ])

    # ★強制1件だけ
    row = rows[0]

    code = row.select_one("td.tac a").text.strip()
    name = row.select_one("th.tal").text.strip()

    tds = row.find_all("td")

    market = tds[0].text.strip()
    price = tds[2].text.strip()
    diff = tds[4].text.strip()
    diff_pct = tds[5].text.replace("%", "").strip()
    trading_value = tds[6].text.replace(",", "").strip()
    per = tds[7].text.strip()
    pbr = tds[8].text.strip()
    yield_ = tds[9].text.strip()

    w.writerow([
        1, code, name, market,
        price, diff, diff_pct,
        trading_value, per, pbr, yield_
    ])

print("DONE ->", csv_path)
