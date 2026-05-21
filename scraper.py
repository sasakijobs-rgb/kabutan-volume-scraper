import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import re
from datetime import timedelta, timezone


def log(msg):
    print(msg)


def get_total_count(text):
    """
    例:
    20件 / 4123件中
    """
    match = re.search(r"/\s*([0-9,]+)件中", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


def parse_page(page, start_no, today, session):

    url = (
        "https://s.kabutan.jp/"
        "warnings/trading_value_ranking/"
        f"?market=all&page={page}"
    )

    response = session.get(url, timeout=30)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("table tbody tr")

    output = []

    for row in rows:

        text = row.get_text(" ", strip=True)

        if not text:
            continue

        # S/K除去
        text = text.replace(" S ", " ")
        text = text.replace(" K ", " ")

        parts = text.split()

        # % / 倍結合
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

    return output, response.text


def main():

    JST = timezone(timedelta(hours=9))
    start_time = datetime.datetime.now(JST)

    today = start_time.strftime("%Y%m%d")

    os.makedirs("output", exist_ok=True)

    csv_file = f"output/trading_value_ranking_{today}.csv"

    log(f"【開始】{start_time.strftime('%H:%M')}")

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    })

    all_data = []

    page = 1
    start_no = 1

    total_count = None
    fetched_count = 0

    while True:

        data, html = parse_page(page, start_no, today, session)

        if not data:
            break

        all_data.extend(data)

        fetched_count = len(all_data)

        # 件数取得（最初だけ）
        if total_count is None:

            match_text = BeautifulSoup(html, "html.parser").get_text(" ", strip=True)

            total_count = get_total_count(match_text)

            log(f"総件数: {total_count}")

        log(f"page {page} done / {fetched_count}件")

        # 次ページ準備
        start_no += len(data)
        page += 1

        # ★最終ページ判定
        if total_count is not None and fetched_count >= total_count:
            break

    # CSV出力
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

        writer.writerows(all_data)

    end_time = datetime.datetime.now(JST)

    duration = end_time - start_time

    log(
        f"【終了】{end_time.strftime('%H:%M')} "
        f"作業時間：合計 {duration.seconds // 60}分"
    )

    log(f"[FILE] {csv_file}")
    log(f"[DONE] {len(all_data)} rows")


if __name__ == "__main__":
    main()
