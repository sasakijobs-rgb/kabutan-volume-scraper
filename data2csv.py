import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import re
from datetime import timedelta, timezone


def log(msg):
    print(msg)


# =========================
# 総件数取得
# =========================
def get_total_count(text):
    match = re.search(r"/\s*([0-9,]+)件中", text)
    if match:
        return int(match.group(1).replace(",", ""))
    return None


# =========================
# ページ解析（修正版）
# =========================
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

    for idx, row in enumerate(rows):

        try:
            # =========================
            # 銘柄（th構造）
            # =========================
            th = row.find("th")
            if not th:
                continue

            name_tag = th.find("p")
            div_tag = th.find("div")

            if not name_tag or not div_tag:
                continue

            name = name_tag.get_text(strip=True)

            parts = div_tag.get_text(" ", strip=True).split()

            if len(parts) >= 2:
                code = parts[0]
                market = parts[1]
            else:
                code = parts[0] if parts else ""
                market = ""

            # =========================
            # 数値（td構造）
            # =========================
            tds = row.find_all("td")

            if len(tds) < 7:
                log(f"[SKIP] page {page} row {idx} td不足")
                continue

            stock_price = tds[0].get_text(strip=True)
            diff_price = tds[1].get_text(" ", strip=True)
            trade_value = tds[2].get_text(strip=True)
            per = tds[4].get_text(strip=True)
            pbr = tds[5].get_text(strip=True)
            yld = tds[6].get_text(strip=True)

            # =========================
            # S / K / プレミアム対策
            # =========================
            diff_price = diff_price.replace("S", "").replace("K", "").strip()

            # =========================
            # rank
            # =========================
            rank_no = start_no + len(output)

            output.append([
                today,
                rank_no,
                name,
                code,
                market,
                stock_price,
                diff_price,
                "",  # 騰落率（必要なら後で追加）
                trade_value,
                per,
                pbr,
                yld
            ])

        except Exception as e:
            log(f"[ERROR] page {page} row {idx}: {e}")
            continue

    return output, response.text


# =========================
# メイン
# =========================
def main():

    JST = timezone(timedelta(hours=9))
    start_time = datetime.datetime.now(JST)
    today = start_time.strftime("%Y%m%d")

    os.makedirs("output", exist_ok=True)

    csv_file = f"output/trading_value_ranking_{today}.csv"

    log("===== START =====")

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        )
    })

    all_data = []
    page = 1
    start_no = 1
    total_count = None

    MAX_PAGE = 300

    while page <= MAX_PAGE:

        data, html = parse_page(page, start_no, today, session)

        if not data:
            log(f"[STOP] page {page} empty")
            break

        all_data.extend(data)

        # 総件数取得
        if total_count is None:
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(" ", strip=True)
            total_count = get_total_count(text)
            log(f"[TOTAL] {total_count}")

        log(f"[PAGE] {page} / COUNT {len(all_data)}")

        start_no += len(data)
        page += 1

        # 終了条件
        if total_count and len(all_data) >= total_count:
            break

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
            "売買代金",
            "PER",
            "PBR",
            "利回り"
        ])

        writer.writerows(all_data)

    log(f"[DONE] {len(all_data)} rows")
    log(f"[FILE] {csv_file}")
    log("===== END =====")


if __name__ == "__main__":
    main()
