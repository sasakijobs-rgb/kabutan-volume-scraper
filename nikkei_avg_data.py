# ###################################
# 日経平均データ取得
# 出力先:
#  output/nikkei_avg_data.csv（最新）
#  output/nikkei_avg_data_merged.csv（履歴追記）
# ###################################

import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import time
import random
import re
from datetime import timedelta, timezone


URL = "https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_DataStoreID=DSWPLETmgR001Control&_ActionID=DefaultAID&burl=iris_indexDetail&cat1=market&cat2=index&dir=tl1-idxdtl%7Ctl2-.N225%7Ctl5-jpn&file=index.html&getFlg=on"


def fetch_nikkei_avg(session):

    for retry in range(3):

        try:
            res = session.get(URL, timeout=30)

            if res.status_code == 200:
                break

            time.sleep(2 + random.random())

        except Exception:
            time.sleep(2 + random.random())

    else:
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    # =========================
    # 現在値ブロック
    # =========================
    price_tag = soup.select_one("#idxdtlPrice em")
    net_change_tag = soup.select_one("#idxdtlNetChange")

    open_tag = soup.select_one("#idxdtlOpen b")
    close_tag = soup.select_one("#idxdtlClose b")
    high_tag = soup.select_one("#idxdtlHigh b")
    low_tag = soup.select_one("#idxdtlLow b")
    year_high_tag = soup.select_one("#idxdtlHighForYear b")
    year_low_tag = soup.select_one("#idxdtlLowForYear b")

    # =========================
    # 日付・時刻抽出
    # 例: (26/06/01 14:58)
    # =========================
    raw_price_text = price_tag.get_text(" ", strip=True) if price_tag else ""

    match = re.search(r"\((\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\)", raw_price_text)

    date_part = ""
    time_part = ""

    if match:
        date_part = match.group(1)
        time_part = match.group(2)

    # 数値だけ抽出（カンマ除去）
    def clean(tag):
        return tag.get_text(strip=True).replace(",", "") if tag else ""

    data = {
        "日付": date_part,
        "時間": time_part,
        "現在値": clean(price_tag).split(" ")[0],
        "前日比": net_change_tag.get_text(" ", strip=True) if net_change_tag else "",
        "始値": clean(open_tag),
        "前日終値": clean(close_tag),
        "高値": clean(high_tag),
        "年初来高値": clean(year_high_tag),
        "安値": clean(low_tag),
        "年初来安値": clean(year_low_tag),
    }

    return data


def write_header(writer):

    writer.writerow([
        "日付",
        "時間",
        "現在値",
        "前日比",
        "始値",
        "前日終値",
        "高値",
        "年初来高値",
        "安値",
        "年初来安値"
    ])


def data_to_row(data):

    return [
        data["日付"],
        data["時間"],
        data["現在値"],
        data["前日比"],
        data["始値"],
        data["前日終値"],
        data["高値"],
        data["年初来高値"],
        data["安値"],
        data["年初来安値"],
    ]


def main():

    JST = timezone(timedelta(hours=9))
    datetime.datetime.now(JST)

    os.makedirs("output", exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept-Language": "ja,en-US;q=0.9",
        "Referer": "https://www.sbisec.co.jp/"
    })

    data = fetch_nikkei_avg(session)

    if not data:
        print("no data")
        return

    row = data_to_row(data)

    # =========================
    # 最新ファイル（上書き）
    # =========================
    latest_file = "output/nikkei_avg_data.csv"

    with open(latest_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        write_header(writer)
        writer.writerow(row)

    # =========================
    # 履歴ファイル（追記）
    # =========================
    merged_file = "output/nikkei_avg_data_merged.csv"
    file_exists = os.path.isfile(merged_file)

    with open(merged_file, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if not file_exists:
            write_header(writer)

        writer.writerow(row)

    print("saved")


if __name__ == "__main__":
    main()
