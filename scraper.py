# scraper.py

import requests
from bs4 import BeautifulSoup
import csv
import datetime
import time


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

            th = row.find("th")

            if not th:
                print(f"[SKIP] row {idx} no th")
                continue

            # 銘柄名
            p_tag = th.find("p")

            if not p_tag:
                print(f"[SKIP] row {idx} no p")
                continue

            name = p_tag.get_text(strip=True)

            # コード・市場
            div_tag = th.find("div")

            if div_tag:
                parts = div_tag.get_text(
                    " ",
                    strip=True
                ).split()
            else:
                parts = []

            if len(parts) >= 2:
                code = parts[0]
                market = parts[1]
            elif len(parts) == 1:
                code = parts[0]
                market = ""
            else:
                code = ""
                market = ""

            # td群
            tds = row.find_all("td")

            if len(tds) < 7:
                print(f"[SKIP] row {idx} td不足")
                continue

            stock_price = (
                tds[0]
                .get_text(strip=True)
                .replace(",", "")
            )

            prev_diff = (
                tds[1]
                .get_text(" ", strip=True)
            )

            trade_value = tds[2].get_text(strip=True)
            per = tds[4].get_text(strip=True)
            pbr = tds[5].get_text(strip=True)
            yld = tds[6].get_text(strip=True)

            raw_data = (
                f"{name} "
                f"{code} "
                f"{market} "
                f"{stock_price} "
                f"{prev_diff} "
                f"{trade_value} "
                f"{per} "
                f"{pbr} "
                f"{yld}"
            )

            rank_no = start_no + len(output)

            output.append([
                today,
                rank_no,
                raw_data
            ])

            print(f"[OK] {rank_no} {name}")

        except Exception as e:

            print(f"[ERROR] row {idx}: {e}")

            continue

        time.sleep(0.05)

    csv_file = (
        f"trading_value_ranking_{today}.csv"
    )

    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "日付",
            "順位",
            "raw_data"
        ])

        writer.writerows(output)

    print(f"[DONE] saved rows: {len(output)}")
    print(f"[FILE] {csv_file}")

    print("===== END =====")


if __name__ == "__main__":
    main()
