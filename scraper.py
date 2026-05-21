import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
from datetime import timedelta, timezone


def log(msg):
    print(msg)


def main(page=1):

    JST = timezone(timedelta(hours=9))
    start_time = datetime.datetime.now(JST)

    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        f"?market=all&page={page}"
    )

    log(f"【開始】{start_time.strftime('%H:%M')}")
    log("")
    log(f"ページ: {page}")
    log(f"{start_time.strftime('%H:%M')} / 取得開始")
    log(url)
    log("")

    try:

        today = start_time.strftime("%Y%m%d")

        os.makedirs("output", exist_ok=True)

        csv_file = f"output/trading_value_ranking_{today}_p{page}.csv"

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

        start_no = 1 + (page - 1) * 20

        for row in rows:

            text = row.get_text(" ", strip=True)

            if not text:
                continue

            # =========================
            # ★重要：ノイズ除去
            # =========================
            text = text.replace(" S ", " ")
            text = text.replace(" K ", " ")

            parts = text.split()

            # % / 倍 結合
            merged = []
            for p in parts:
                if p in ["%", "倍"]:
                    if merged:
                        merged[-1] += p
                else:
                    merged.append(p)

            parts = merged

            # 見出し・壊れ行除外
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

            # ★追加安全チェック（ズレ防止）
            if not stock_price.replace(",", "").replace(".", "").replace("-", "").isdigit():
                continue

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
        # CSV出力
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

        log(
            f"【終了】{end_time.strftime('%H:%M')}  "
            f"作業時間：合計 {duration.seconds // 60}分"
        )

        log(f"[FILE] {csv_file}")
        log(f"[DONE] {len(output)} rows")

    except Exception as e:

        end_time = datetime.datetime.now(JST)

        log(f"【エラー終了】{end_time.strftime('%H:%M')}")
        log(f"エラー内容：{e}")
        log("作業は途中で停止しました")

        raise


if __name__ == "__main__":

    main(page=1)
