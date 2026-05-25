
自分に合った回答を得る

ログインすると、保存済みチャットに基づく回答に加えて、画像作成やファイルのアップロードも利用できます。


ログイン
次のプログラムを参考に日経VIのページから値をスクレイピングしてください
出力先は同じoutputフォルダへ
必要な項目は下記で
取得元は下記で
https://indexes.nikkei.co.jp/nkave/index/profile?idx=nk225vi

必要項目と取得テーブルは下記で

【テーブル】individual-value
日付：datedtime
値：price
前日比(率)：rate
前日比(値)：diff
始値：open_price
始値(時)：opentime
高値：high_price
高値(時)：hightime
安値：low_price
安値(時)：lowtime

<div class="individual-value">
                <div>
                    <div class="current" id="price">33.15</div>
                    <div class="daily-change up" id="updown_class">
                        <span class="range" id="rate">+16.93%</span>
                        <span class="change" id="diff">+4.80</span>
                        <span class="date" id="datedtime">2026.05.25(12:46)</span>
                    </div>
                </div>
                    <div class="ohl">
                        <table class="ohl-table">
                            <tbody><tr>
                                <th class="label">始値</th>
                                <td class="value" id="open_price">32.61</td>
                                <td class="date" id="opentime">(09:00)</td>
                            </tr>
                            <tr>
                                <th class="label">高値</th>
                                <td class="value" id="high_price">33.39</td>
                                <td class="date" id="hightime">(12:18)</td>
                            </tr>
                            <tr>
                                <th class="label">安値</th>
                                <td class="value" id="low_price">27.89</td>
                                <td class="date" id="lowtime">(10:32)</td>
                            </tr>
                        </tbody></table>
                    </div>
            </div>

import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import re
import time
import random
import logging
from datetime import timedelta, timezone


def log(msg):
    print(msg)


def get_total_count(text):

    match = re.search(r"([0-9,]+)\s*件\s*/\s*([0-9,]+)\s*件中", text)

    if match:
        return int(match.group(2).replace(",", ""))

    return None


def parse_page(page, start_no, today, session):

    url = (
        "https://s.kabutan.jp/"
        f"warnings/trading_value_ranking/?market=all&page={page}"
    )

    # =========================
    # リトライ
    # =========================
    for retry in range(3):

        response = session.get(url, timeout=30)

        if response.status_code == 200:
            break

        # 終端ページ
        if response.status_code in [403, 404, 405]:

            log(f"[STOP] page {page} status {response.status_code}")

            logging.info(f"[STOP] page {page} status {response.status_code}")

            return [], ""

        log(f"[WARN] page {page} status {response.status_code} retry {retry+1}")

        logging.info(f"[WARN] page {page} status {response.status_code} retry {retry+1}")

        time.sleep(2 + random.random())

    else:
        return [], ""

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("table tbody tr")

    output = []

    for row in rows:

        text = row.get_text(" ", strip=True)

        if not text:
            continue

        # =========================
        # ノイズ除去
        # =========================
        text = text.replace("かぶたん プレミアム", "")
        text = text.replace(" S ", " ")
        text = text.replace(" K ", " ")

        parts = text.split()

        # =========================
        # % / 倍 を結合
        # =========================
        merged = []

        for p in parts:

            if p in ["%", "倍"]:

                if merged:
                    merged[-1] += p

            else:
                merged.append(p)

        parts = merged

        # =========================
        # 状態列抽出
        # =========================
        status = ""

        status_tokens = [
            "Ｓ",
            "ケ",
            "Sｹ",
            "S",
            "K"
        ]

        cleaned = []

        for p in parts:

            if p in status_tokens:
                status = p
            else:
                cleaned.append(p)

        parts = cleaned

        # =========================
        # 列数チェック
        # =========================
        if len(parts) < 10:

            log(f"[SKIP] len error : {parts}")

            logging.info(f"[SKIP] len error : {parts}")

            continue

        try:

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

        except Exception as e:

            log(f"[SKIP] parse error : {parts}")

            logging.error(f"[SKIP] parse error : {parts} {e}")

            continue

        # =========================
        # 株価チェック
        # =========================
        stock_price_check = (
            stock_price
            .replace(",", "")
            .replace(".", "")
            .replace("-", "")
        )

        if not stock_price_check.isdigit():

            log(f"[SKIP] stock price error : {parts}")

            logging.info(f"[SKIP] stock price error : {parts}")

            continue

        rank_no = start_no + len(output)

        output.append([
            today,
            rank_no,
            name,
            code,
            market,
            status,
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

    # =========================
    # logging設定（追加のみ）
    # =========================
    os.makedirs("output", exist_ok=True)

    logging.basicConfig(
        filename=f"output/log_{today}.log",
        level=logging.INFO,
        format="%(asctime)s %(message)s",
        encoding="utf-8"
    )

    print(f"start {start_time.strftime('%Y/%m/%d %H:%M')}")

    logging.info(f"start {start_time.strftime('%Y/%m/%d %H:%M')}")

    os.makedirs("output", exist_ok=True)

    csv_file = f"output/trading_value_ranking_{today}.csv"

    log(f"===== START {start_time.strftime('%H:%M')} =====")

    logging.info(f"===== START {start_time.strftime('%H:%M')} =====")

    session = requests.Session()

    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept-Language": "ja,en-US;q=0.9",
        "Referer": "https://s.kabutan.jp/"
    })

    all_data = []

    page = 1
    start_no = 1

    total_count = None

    while True:

        log(f"[PAGE] {page}")

        logging.info(f"[PAGE] {page}")

        data, html = parse_page(
            page,
            start_no,
            today,
            session
        )

        # =========================
        # 終了
        # =========================
        if not data:

            log("[STOP] no data")

            logging.info("[STOP] no data")

            break

        all_data.extend(data)

        current_time = datetime.datetime.now(JST).strftime("%H:%M")

        print(
            f"{len(all_data)}件 / {total_count or '?'}件中 "
            f"{current_time}"
        )

        logging.info(
            f"{len(all_data)}件 / {total_count or '?'}件中 "
            f"{current_time}"
        )

        # =========================
        # 総件数取得
        # =========================
        if total_count is None:

            text = BeautifulSoup(
                html,
                "html.parser"
            ).get_text(" ", strip=True)

            total_count = get_total_count(text)

            log(f"[TOTAL] {total_count}")

            logging.info(f"[TOTAL] {total_count}")

        log(f"[COUNT] {len(all_data)}")

        logging.info(f"[COUNT] {len(all_data)}")

        start_no += len(data)

        page += 1

        # =========================
        # 終了条件
        # =========================
        if total_count and len(all_data) >= total_count:

            log("[STOP] total reached")

            logging.info("[STOP] total reached")

            break

        # =========================
        # 通常スリープ
        # =========================
        time.sleep(random.uniform(0.5, 1.5))

        # =========================
        # 2000件ごと休憩
        # =========================
        if len(all_data) % 2000 < len(data):

            sleep_sec = 180 + random.randint(-30, 30)

            log(f"[SLEEP] 2000件到達 -> {sleep_sec}秒休憩")

            logging.info(f"[SLEEP] 2000件到達 -> {sleep_sec}秒休憩")

            time.sleep(sleep_sec)

    # =========================
    # CSV出力
    # =========================
    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        writer.writerow([
            "日付",
            "順位",
            "銘柄名",
            "コード",
            "市場",
            "状態",
            "株価",
            "前日差",
            "騰落率",
            "売買代金",
            "PER",
            "PBR",
            "配当利回り"
        ])

        writer.writerows(all_data)

    end_time = datetime.datetime.now(JST)

    duration = end_time - start_time

    log(f"===== END {end_time.strftime('%H:%M')} =====")

    logging.info(f"===== END {end_time.strftime('%H:%M')} =====")

    log(f"[FILE] {csv_file}")

    logging.info(f"[FILE] {csv_file}")

    log(f"[ROWS] {len(all_data)}")

    logging.info(f"[ROWS] {len(all_data)}")

    log(f"[TIME] {duration.seconds // 60}分")

    logging.info(f"[TIME] {duration.seconds // 60}分")

    print(f"\nend {end_time.strftime('%Y/%m/%d %H:%M')}")


if __name__ == "__main__":
    main()

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
    # CSV出力
    # =========================
    csv_file = f"output/nikkei_vi_{today}.csv"

    with open(
        csv_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

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

nikkei_vi_data.csvへ追記していくようにできますか？

はい、可能です。
w モードではなく a（追記）モードで開き、ファイルが存在しない場合のみヘッダーを書き込むように変更します。

CSV出力部分を下記へ置き換えてください。

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
これで実行するたびに

output/nikkei_vi_data.csv
へ1行ずつ追加されます。



音声
当社では cookies を使用しています

Cookie はサイトの機能維持、利用状況の測定、マーケティング支援に役立ちます。Cookie の設定はいつでも管理できます。詳しくは Cookie ポリシーをご覧ください。


必須項目以外を拒否する

すべて受け入れる
