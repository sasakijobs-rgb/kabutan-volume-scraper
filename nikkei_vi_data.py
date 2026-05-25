# ###################################
# 日経平均ボラティリティー・インデックス
# （上記のサイトからVI情報を取得）
# 出力先:output/nikkei_vi_data.csv
# ###################################
import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import time
import random
import logging
from datetime import timedelta, timezone


def log(msg):
    print(msg)


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

            log(
                f"[WARN] status {response.status_code} "
                f"retry {retry + 1}"
            )

            logging.info(
                f"[WARN] status {response.status_code} "
                f"retry {retry + 1}"
            )

            time.sleep(2 + random.random())

        except Exception as e:

            log(f"[ERROR] request error retry {retry + 1} {e}")

            logging.error(
                f"[ERROR] request error retry {retry + 1} {e}"
            )

            time.sleep(2 + random.random())

    else:

        return None

    soup = BeautifulSoup(response.text, "html.parser")

    table = soup.select_one("div.individual-value")

    if not table:

        log("[ERROR] individual-value not found")

        logging.error("[ERROR] individual-value not found")

        return None

    def get_text_by_id(tag_id):

        tag = table.select_one(f"#{tag_id}")

        if tag:
            return tag.get_text(strip=True)

        return ""

    data = {
        "日付": get_text_by_id("datedtime"),
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


def main():

    JST = timezone(timedelta(hours=9))

    start_time = datetime.datetime.now(JST)

    today = start_time.strftime("%Y%m%d")

    # =========================
    # outputフォルダ
    # =========================
    os.makedirs("output", exist_ok=True)

    # =========================
    # logging設定
    # =========================
    logging.basicConfig(
        filename=f"output/log_nikkei_vi_{today}.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        encoding="utf-8"
    )

    log(f"===== START {start_time.strftime('%H:%M')} =====")

    logging.info(
        f"===== START {start_time.strftime('%H:%M')} ====="
    )

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

        log("[ERROR] no data")

        logging.error("[ERROR] no data")

        return

    # =========================
    # CSV出力（追記）
    # =========================
    csv_file = "output/nikkei_vi_data.csv"

    file_exists = os.path.isfile(csv_file)

    with open(
        csv_file,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        # =========================
        # 初回のみヘッダー
        # =========================
        if not file_exists:

            writer.writerow([
                "日付",
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

        # =========================
        # データ追記
        # =========================
        writer.writerow([
            data["日付"],
            data["値"],
            data["前日比(率)"],
            data["前日比(値)"],
            data["始値"],
            data["始値(時)"],
            data["高値"],
            data["高値(時)"],
            data["安値"],
            data["安値(時)"]
        ])

    # =========================
    # 終了ログ
    # =========================
    end_time = datetime.datetime.now(JST)

    duration = end_time - start_time

    log(f"===== END {end_time.strftime('%H:%M')} =====")

    logging.info(
        f"===== END {end_time.strftime('%H:%M')} ====="
    )

    log(f"[FILE] {csv_file}")

    logging.info(f"[FILE] {csv_file}")

    log(f"[TIME] {duration.seconds}秒")

    logging.info(f"[TIME] {duration.seconds}秒")

    print(f"\nend {end_time.strftime('%Y/%m/%d %H:%M')}")


if __name__ == "__main__":
    main()
