import requests
from bs4 import BeautifulSoup
import csv
import os
import re
from datetime import datetime, timezone, timedelta


URL = "https://shikiho.toyokeizai.net/market/N225"


def fetch_nikkei(session):

    try:
        res = session.get(URL, timeout=30)
        if res.status_code != 200:
            return None

    except Exception:
        return None

    soup = BeautifulSoup(res.text, "html.parser")

    # =========================
    # メインブロック
    # =========================
    block = soup.select_one("div.basic-section")

    if not block:
        return None

    def get_text(selector):
        tag = block.select_one(selector)
        return tag.get_text(strip=True) if tag else ""

    # =========================
    # 現在値
    # =========================
    current = block.select_one(".basic-section__price__current")
    current_value = current.get_text(strip=True) if current else ""

    change = block.select_one(".basic-section__price__change")
    change_value = change.get_text(" ", strip=True) if change else ""

    # =========================
    # dt/dd構造（重要）
    # =========================
    items = block.select("dl dt")

    data_map = {}

    for dt in items:
        key = dt.get_text(strip=True)
        dd = dt.find_next_sibling("dd")
        value = dd.get_text(" ", strip=True) if dd else ""
        data_map[key] = value

    # =========================
    # 日付・時間（更新日時）
    # =========================
    update_time = ""
    update_tag = block.select_one(".basic-section__top__update__time")
    if update_tag:
        update_time = update_tag.get_text(" ", strip=True)

    # =========================
    # 高値/安値の時間抽出
    # =========================
    def split_price_time(text):
        m = re.search(r"([\d,\.]+)\s*\((\d{2}:\d{2})\)", text)
        if m:
            return m.group(1), m.group(2)
        return text, ""

    high_price, high_time = split_price_time(data_map.get("高値", ""))
    low_price, low_time = split_price_time(data_map.get("安値", ""))

    open_price, open_time = split_price_time(data_map.get("始値", ""))

    data = {
        "更新日時": update_time,
        "現在値": current_value,
        "前日比": change_value,
        "始値": open_price,
        "始値(時)": open_time,
        "高値": high_price,
        "高値(時)": high_time,
        "安値": low_price,
        "安値(時)": low_time,
        "年初来高値": data_map.get("年初来高値", ""),
        "年初来安値": data_map.get("年初来安値", ""),
        "出来高": data_map.get("出来高", ""),
        "売買代金": data_map.get("売買代金", ""),
        "年初来上昇率": data_map.get("年初来株価上昇率", ""),
        "乖離率": data_map.get("200日移動平均乖離率", ""),
    }

    return data


def write_header(w):

    w.writerow([
        "更新日時",
        "現在値",
        "前日比",
        "始値",
        "始値(時)",
        "高値",
        "高値(時)",
        "安値",
        "安値(時)",
        "年初来高値",
        "年初来安値",
        "出来高",
        "売買代金",
        "年初来上昇率",
        "乖離率"
    ])


def data_to_row(d):

    return [
        d["更新日時"],
        d["現在値"],
        d["前日比"],
        d["始値"],
        d["始値(時)"],
        d["高値"],
        d["高値(時)"],
        d["安値"],
        d["安値(時)"],
        d["年初来高値"],
        d["年初来安値"],
        d["出来高"],
        d["売買代金"],
        d["年初来上昇率"],
        d["乖離率"],
    ]


def main():

    os.makedirs("output", exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ja,en-US;q=0.9",
        "Referer": "https://shikiho.toyokeizai.net/"
    })

    data = fetch_nikkei(session)

    if not data:
        print("no data")
        return

    row = data_to_row(data)

    file_path = "output/nikkei_avg_data.csv"
    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        if not file_exists:
            write_header(w)

        w.writerow(row)

    print("saved")


if __name__ == "__main__":
    main()
