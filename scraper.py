import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
from datetime import timedelta, timezone


def log(msg):
    print(msg)


def main():

    JST = timezone(timedelta(hours=9))

    start_time = datetime.datetime.now(JST)

    # =========================
    # START DISPLAY
    # =========================
    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        "?market=all&page=1"
    )

    log("【開始】" + start_time.strftime("%H:%M"))
    log("")
    log(f"20件 / 4123件中 {start_time.strftime('%H:%M')}")
    log(url)
    log("")

    try:

        today = start_time.strftime("%Y%m%d")

        os.makedirs("output", exist_ok=True)

        csv_file = f"output/trading_value_ranking_{today}.csv"

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

        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("table tbody tr")

        output = []
        start_no = 4141

        for idx, row in enumerate(rows):

            text = row.get_text(" ", strip=True)

            if not text:
                continue

            parts = text.split()

            merged = []
            for p in parts:
                if p in ["%", "倍"]:
                    if merged:
                        merged[-1] += p
                else:
                    merged.append(p)

            parts = merged

            if len(parts) < 10:
                continue

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

        # =========================
        # CSV OUTPUT
        # =========================
        with open(csv_file, "w", newline="", encoding="utf-8-sig") as f:

            writer = csv.writer(f)

            writer.writerow([
                "日付",
                "順位",
                "銘柄名",
                "コード",
                "市場",
                "株価",
                "前日差",
                "騰落率",
                "出来高",
                "PER",
                "PBR",
                "配当利回り"
            ])

            writer.writerows(output)

        end_time = datetime.datetime.now(JST)

        duration = end_time - start_time

        # =========================
        # END DISPLAY（正常）
        # =========================
        msg = (
            f"【終了】{end_time.strftime('%H:%M')}  "
            f"作業時間：合計 {duration.seconds // 60}分"
        )

        log(msg)
        log(msg)  # ログにも同じ内容

        log(f"[FILE] {csv_file}")
        log(f"[DONE] {len(output)} rows")

    except Exception as e:

        end_time = datetime.datetime.now(JST)

        log("【エラー終了】" + end_time.strftime("%H:%M"))
        log(f"エラー内容：{e}")
        log("作業は途中で停止しました")

        raise


if __name__ == "__main__":
    main()
