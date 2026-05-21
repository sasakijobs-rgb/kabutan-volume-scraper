# scraper.py

import requests
from bs4 import BeautifulSoup
import csv
import datetime
import re


def main():

    print("===== START =====")

    today = datetime.datetime.now().strftime("%Y%m%d")

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

    response = requests.get(
        url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    print(f"[INFO] status: {response.status_code}")

    soup = BeautifulSoup(
        response.text,
        "html.parser"
    )

    rows = soup.select("table tbody tr")

    print(f"[INFO] raw rows: {len(rows)}")

    output = []

    start_no = 4141

    for idx, row in enumerate(rows):

        try:

            # 行全体テキスト
            text = row.get_text(
                " ",
                strip=True
            )

            # 空行除外
            if not text:
                continue

            print(f"[ROW {idx}] {text}")

            # 分割
            parts = text.split()

            # 最低必要数
            if len(parts) < 9:
                print(f"[SKIP] row {idx} parts不足")
                continue

            # 例:
            # ウチヤマＨＤ 6059 東S 342 -2 -0.58% 1 22.7倍 0.46倍 2.92%

            name = parts[0]
            code = parts[1]
            market = parts[2]
            stock_price = parts[3]
            diff_price = parts[4]
            diff_percent = parts[5]
            trade_value = parts[6]
            per = parts[7]
            pbr = parts[8]

            if len(parts) >= 10:
                yld = parts[9]
            else:
                yld = ""

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

    csv_file = (
        f"trading_value_ranking_{today}.csv"
    )

    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

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
