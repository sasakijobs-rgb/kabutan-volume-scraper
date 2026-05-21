import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import re
from datetime import timedelta, timezone


def main():

    print("===== START =====")

    # JSTで日付生成（重要）
    JST = timezone(timedelta(hours=9))
    today = datetime.datetime.now(JST).strftime("%Y%m%d")

    # 出力フォルダ作成
    os.makedirs("output", exist_ok=True)

    csv_file = f"output/trading_value_ranking_{today}.csv"

    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        "?market=all&page=207"
    )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    }

    response = requests.get(url, headers=headers, timeout=30)
    response.raise_for_status()

    print(f"[INFO] status: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("table tbody tr")

    print(f"[INFO] raw rows: {len(rows)}")

    output = []

    start_no = 4141

    for idx, row in enumerate(rows):

        try:
            text = row.get_text(" ", strip=True)

            if not text:
                continue

            print(f"[ROW {idx}] {text}")

            # 市場区分説明などを除外
            if "東証" in text or "名証" in text or "札証" in text or "福証" in text:
                print(f"[SKIP] row {idx} market label")
                continue

            parts = text.split()

            # % と 倍 を結合
            merged = []
            for p in parts:
                if p in ["%", "倍"]:
                    if merged:
                        merged[-1] += p
                else:
                    merged.append(p)

            parts = merged

            # 最低チェック
            if len(parts) < 10:
                print(f"[SKIP] row {idx} parts不足: {parts}")
                continue

            # データ分解
            name = parts[0]
            code = parts[1]
            market = parts[2]
            stock_price = parts[3]
            diff_price = parts[4]
            diff_percent = parts[5]
            trade_value = parts[6]
            per = parts[7]
            pbr = parts[8]
            yld = parts[9]

            rank_no = start_no + len(output)

            output.append([
                today,
                rank_no,
                name,
                code,
                market,
                stock_price,
                diff_price,
                diff_percent,
                trade_value,
                per,
                pbr,
                yld
            ])

            print(f"[OK] {rank_no} {name}")

        except Exception as e:
            print(f"[ERROR] row {idx}: {e}")
            continue

    # CSV出力
    with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        writer.writerow([
            "date",
            "rank",
            "name",
            "code",
            "market",
            "stock_price",
            "diff_price",
            "diff_percent",
            "trade_value",
            "PER",
            "PBR",
            "yield"
        ])

        writer.writerows(output)

    print(f"[DONE] saved rows: {len(output)}")
    print(f"[FILE] {csv_file}")
    print("===== END =====")


if __name__ == "__main__":
    main()
