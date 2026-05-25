# ###################################
# 日経平均ボラティリティー・インデックス
# （上記のサイトからVI情報を取得）
# 出力先:output/nikkei_vi_data.csvへ毎日追記
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


def fetch_nikkei_vi(session):

    url = "https://indexes.nikkei.co.jp/nkave/index/profile?idx=nk225vi"

    # =========================
    # リトライ
    # =========================
    for retry in range(3):

        try:

            response = session.get(url, timeout=30)

            if response.status_code == 200:
                break

            time.sleep(2 + random.random())

        except Exception:

            time.sleep(2 + random.random())

    else:

        return None

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.select_one("div.individual-value")

    if not table:
        return None

    def get_text_by_id(tag_id):

        tag = table.select_one(f"#{tag_id}")

        if tag:
            return tag.get_text(strip=True)

        return ""

    # =========================
    # 日付・時間分割
    # 2026.05.25(13:08)
    # =========================
    raw_datetime = get_text_by_id("datedtime")

    date_part = ""
    time_part = ""

    match = re.search(
        r"(\d{4}\.\d{2}\.\d{2})\((\d{2}:\d{2})\)",
        raw_datetime
    )

    if match:

        date_part = match.group(1)
        time_part = match.group(2)

    data = {
        "日付": date_part,
        "時間": time_part,
        "値": get_text_by_id("price"),
        "前日比(率)": get_text_by_id("rate"),
        "前日比(値)": get_text_by_id("diff"),
        "始値": get_text_by_id("open_price"),
        "始値(時)": get_text_by_id("opentime"),
        "高値": get_text_by_id("high_price"),
        "高値(時)": get_text_by_id("hightime"),
        "安値": get_text_by_id("low_price"),
        "安値(時)": get_text_by_id("lowtime"),
    }

    return data


def write_header(writer):

    writer.writerow([
        "日付",
        "時間",
        "値",
        "前日比(率)",
        "前日比(値)",
        "始値",
        "始値(時)",
        "高値",
        "高値(時)",
        "安値",
        "安値(時)"
    ])


def data_to_row(data):

    return [
        data["日付"],
        data["時間"],
        data["値"],
        data["前日比(率)"],
        data["前日比(値)"],
        data["始値"],
        data["始値(時)"],
        data["高値"],
        data["高値(時)"],
        data["安値"],
        data["安値(時)"]
    ]


def main():

    JST = timezone(timedelta(hours=9))

    datetime.datetime.now(JST)

    # =========================
    # outputフォルダ
    # =========================
    os.makedirs("output", exist_ok=True)

    # =========================
    # session
    # =========================
    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept-Language": "ja,en-US;q=0.9",
        "Referer": "https://indexes.nikkei.co.jp/"
    })

    # =========================
    # データ取得
    # =========================
    data = fetch_nikkei_vi(session)

    if not data:

        print("no data")

        return

    row = data_to_row(data)

    # ==================================================
    # 1. 最新のみ保持（毎回上書き）
    # ==================================================
    latest_file = "output/nikkei_vi_data.csv"

    with open(
        latest_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        write_header(writer)

        writer.writerow(row)

    # ==================================================
    # 2. 履歴保存（追記）
    # ==================================================
    merged_file = "output/nikkei_vi_data_merged.csv"

    file_exists = os.path.isfile(merged_file)

    with open(
        merged_file,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        # 初回のみヘッダー
        if not file_exists:

            write_header(writer)

        writer.writerow(row)

    print("saved")


if __name__ == "__main__":
    main()
