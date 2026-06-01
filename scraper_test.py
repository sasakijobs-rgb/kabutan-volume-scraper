import os
import csv
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime


URL = "https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_DataStoreID=DSWPLETmgR001Control&_ActionID=DefaultAID&burl=iris_indexDetail&cat1=market&cat2=index&dir=tl1-idxdtl%7Ctl2-.N225%7Ctl5-jpn&file=index.html&getFlg=on"


def fetch():

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ja,en-US;q=0.9"
    })

    res = session.get(URL, timeout=30)
    res.raise_for_status()

    soup = BeautifulSoup(res.text, "html.parser")

    price_tag = soup.select_one("#idxdtlPrice em")
    net_change_tag = soup.select_one("#idxdtlNetChange")
    open_tag = soup.select_one("#idxdtlOpen b")
    close_tag = soup.select_one("#idxdtlClose b")
    high_tag = soup.select_one("#idxdtlHigh b")
    low_tag = soup.select_one("#idxdtlLow b")

    raw = price_tag.get_text(" ", strip=True) if price_tag else ""

    m = re.search(r"\((\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\)", raw)

    date, time = ("", "")
    if m:
        date, time = m.group(1), m.group(2)

    def clean(x):
        return x.get_text(strip=True).replace(",", "") if x else ""

    return [
        date,
        time,
        clean(price_tag).split(" ")[0] if price_tag else "",
        net_change_tag.get_text(" ", strip=True) if net_change_tag else "",
        clean(open_tag),
        clean(close_tag),
        clean(high_tag),
        clean(low_tag),
    ]


def save(row):

    os.makedirs("output", exist_ok=True)

    file_path = "output/nikkei_avg_data.csv"

    file_exists = os.path.isfile(file_path)

    with open(file_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "日付",
                "時間",
                "現在値",
                "前日比",
                "始値",
                "前日終値",
                "高値",
                "安値"
            ])

        writer.writerow(row)


def main():

    row = fetch()
    save(row)

    print("saved:", datetime.now())


if __name__ == "__main__":
    main()
