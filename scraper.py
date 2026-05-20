import re
import csv
import time
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://s.kabutan.jp/warnings/trading_value_ranking/"
DATE = "20260520"
OUTPUT_FILE = f"trading_value_ranking_{DATE}.csv"


# =========================
# 件数から最終ページ計算
# =========================
def calc_last_page(total_items, per_page=20):
    return (total_items + per_page - 1) // per_page


# =========================
# 件数取得（ページ1から）
# =========================
def get_total_count():
    url = BASE_URL + "?market=all&page=1"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    text = soup.get_text()

    # 例: "4143件 / 4143件中"
    m = re.search(r"([\d,]+)件\s*/\s*([\d,]+)件中", text)
    if not m:
        raise Exception("件数が取得できませんでした")

    total = int(m.group(2).replace(",", ""))
    return total


# =========================
# 通常ページ（1ページ目）
# =========================
def parse_page1():
    url = BASE_URL + "?market=all&page=1"
    r = requests.get(url, timeout=10)
    soup = BeautifulSoup(r.text, "html.parser")

    rows = []

    table = soup.select("table tbody tr")
    no = 1

    for tr in table:
        tds = tr.find_all(["td", "th"])
        if len(tds) < 8:
            continue

        try:
            name_block = tds[0].get_text(" ", strip=True)
            parts = name_block.split()

            name = parts[0]
            code = parts[1]
            market = parts[2]

            price = tds[1].get_text(strip=True)
            change = tds[2].get_text(" ", strip=True).split()[0]
            change_pct = tds[2].get_text(" ", strip=True).split()[1]

            volume = tds[3].get_text(strip=True)
            per = tds[5].get_text(strip=True)
            pbr = tds[6].get_text(strip=True)
            yield_ = tds[7].get_text(strip=True)

            rows.append([
                DATE,
                no,
                code,
                name,
                market,
                price,
                change,
                change_pct,
                volume,
                per,
                pbr,
                yield_
            ])
            no += 1

        except:
            continue

    return rows


# =========================
# 最終ページ（崩れHTML対応）
# =========================
def parse_last_page(page):
    url = BASE_URL + f"?market=all&page={page}"
    r = requests.get(url, timeout=10)

    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text("\n", strip=True)

    rows = []
    no = 4141  # 必要なら調整（後で連番でもOK）

    # 1行単位で粗抽出
    lines = text.split("\n")

    for line in lines:
        # 例:
        # ウチヤマＨＤ 6059 東S 342 -2 -0.58% 1 22.7倍 0.46倍 2.92%
        if not re.search(r"\d{4}\s", line):
            continue

        parts = line.split()

        if len(parts) < 9:
            continue

        try:
            name = parts[0]
            code = parts[1]
            market = parts[2]
            price = parts[3]
            change = parts[4]
            change_pct = parts[5]
            volume = parts[6]
            per = parts[7]
            pbr = parts[8]
            yield_ = parts[9] if len(parts) > 9 else "-"

            rows.append([
                DATE,
                no,
                code,
                name,
                market,
                price,
                change,
                change_pct,
                volume,
                per,
                pbr,
                yield_
            ])
            no += 1

        except:
            continue

    return rows


# =========================
# CSV出力
# =========================
def save_csv(rows):
    header = [
        "日付","No","コード","銘柄名","市場",
        "株価(百万円)","前日比","前日比(%)",
        "売買代金","PER","PBR","利回り"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# =========================
# MAIN
# =========================
def main():
    print("===== START =====")

    total = get_total_count()
    last_page = calc_last_page(total, 20)

    print(f"[INFO] total items: {total}")
    print(f"[INFO] last page: {last_page}")

    all_rows = []

    # 1ページ目
    print("[PAGE] 1")
    rows1 = parse_page1()
    all_rows.extend(rows1)

    # 最終ページ
    print(f"[PAGE] {last_page}")
    rows_last = parse_last_page(last_page)
    all_rows.extend(rows_last)

    save_csv(all_rows)

    print("===== DONE =====")
    print(f"output: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
