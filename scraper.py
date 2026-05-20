import csv
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=208"
OUTPUT_FILE = f"output/page208_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"


def is_valid_row(text):
    if not text:
        return False
    if len(text) < 10:
        return False
    if "表示モード" in text:
        return False
    if "銘柄" in text:
        return False
    return True


def run():
    print("===== START =====")
    print(f"URL: {URL}")

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get(URL)
    time.sleep(3)

    rows = driver.find_elements(By.TAG_NAME, "tr")

    print(f"[INFO] rows detected: {len(rows)}")

    data = []

    for r in rows:
        txt = r.text.strip()

        print("\n===== RAW ROW =====")
        print(txt)

        if is_valid_row(txt):
            data.append(txt)

    driver.quit()

    # CSV出力
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["page", "raw_data"])

        for row in data:
            writer.writerow([208, row])

    print("\n===== DONE =====")
    print(f"saved rows: {len(data)}")
    print(f"file: {OUTPUT_FILE}")
    print("===== END =====")


if __name__ == "__main__":
    run()
