import requests
from bs4 import BeautifulSoup
import csv
from datetime import datetime
import os

FOLDER = "output"
os.makedirs(FOLDER, exist_ok=True)

TOTAL_PAGES = 2
TOP_N = 3000  # 戻す

BASE_URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&stc=&stm=0&page="

today = datetime.now().strftime("%Y%m%d")
csv_path = os.path.join(FOLDER, f"trading_value_ranking_{today}.csv")

headers = {
    "User-Agent": "Mozilla/5.0"
}

def clean(text):
    return text.replace("\n", "").replace("\t", "").strip()

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)

    writer.writerow([
        "No","コード","銘柄名","市場","株価",
        "前日比","前日比(%)","売買代金",
        "PER","PBR","利回り"
    ])

    rank = 1

    for page in range(1, TOTAL_PAGES + 1):

        url = BASE_URL + str(page)
        print("GET:", url)

        res = requests.get(url, headers=headers, timeout=20)

        # ★403対策チェック
        if "403 Forbidden" in res.text:
            print("403検知 → 終了")
            break

        soup = BeautifulSoup(res.text, "html.parser")

        table = soup.select_one("table.stock_table.st_market")
        if not table:
            print("tableなし")
            continue

        rows = table.select("tbody tr")

        print("rows:", len(rows))

        for row in rows:

            # 余計な行除外（重要）
            if row.find("th") is None:
                continue

            code_td = row.select_one("td.tac a")
            name_th = row.select_one("th.tal")

            tds = row.find_all("td")

            if not code_td or not name_th:
                continue

            try:
                code = clean(code_td.text)
                name = clean(name_th.text)

                # tdの構造は固定（あなたのHTMLベース）
                # [0]=市場, [2]=株価, [4]=前日比, [5]=%, [6]=売買代金, [7]=PER, [8]=PBR, [9]=利回り
                market = clean(tds[0].text)
                price = clean(tds[2].text)

                diff = clean(tds[4].text)
                diff_pct = clean(tds[5].text).replace("%", "")
                trading_value = clean(tds[6].text).replace(",", "")

                per = clean(tds[7].text)
                pbr = clean(tds[8].text)
                yield_ = clean(tds[9].text)

                writer.writerow([
                    rank, code, name, market,
                    price, diff, diff_pct,
                    trading_value, per, pbr, yield_
                ])

                rank += 1

                if rank > TOP_N:
                    break

            except Exception as e:
                print("error:", e)
                continue

        if rank > TOP_N:
            break

print("done:", csv_path)
