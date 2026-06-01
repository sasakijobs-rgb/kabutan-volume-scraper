import csv
import os
import re
from playwright.sync_api import sync_playwright


URL = "https://www.sbisec.co.jp/ETGate/?_ControlID=WPLETmgR001Control&_PageID=WPLETmgR001Mdtl20&_DataStoreID=DSWPLETmgR001Control&_ActionID=DefaultAID&burl=iris_indexDetail&cat1=market&cat2=index&dir=tl1-idxdtl%7Ctl2-.N225%7Ctl5-jpn&file=index.html&getFlg=on"


def fetch():

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto(URL, wait_until="networkidle")

        # 明示的に要素待ち（JS描画対策）
        page.wait_for_selector("#idxdtlPrice em")

        raw_price = page.locator("#idxdtlPrice em").inner_text()
        net_change = page.locator("#idxdtlNetChange").inner_text()

        open_ = page.locator("#idxdtlOpen b").inner_text()
        close = page.locator("#idxdtlClose b").inner_text()
        high = page.locator("#idxdtlHigh b").inner_text()
        low = page.locator("#idxdtlLow b").inner_text()

        browser.close()

    # 日付・時間抽出
    m = re.search(r"\((\d{2}/\d{2}/\d{2})\s+(\d{2}:\d{2})\)", raw_price)

    date, time = ("", "")
    if m:
        date, time = m.group(1), m.group(2)

    price = raw_price.split(" ")[0] if raw_price else ""

    return [
        date,
        time,
        price,
        net_change,
        open_,
        close,
        high,
        low
    ]


def save(row):

    os.makedirs("output", exist_ok=True)

    path = "output/nikkei_avg_data.csv"
    exists = os.path.isfile(path)

    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        if not exists:
            w.writerow([
                "日付",
                "時間",
                "現在値",
                "前日比",
                "始値",
                "前日終値",
                "高値",
                "安値"
            ])

        w.writerow(row)


def main():

    row = fetch()
    save(row)

    print("saved")


if __name__ == "__main__":
    main()
