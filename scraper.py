import os
import time
import random
import csv
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

BASE_URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page={}"
MAX_PAGES = 300

today = datetime.now().strftime("%Y%m%d")

os.makedirs("output", exist_ok=True)

output_file = f"output/trading_value_ranking_{today}.csv"

header = [
    "日付","順位","コード","銘柄名","市場",
    "株価","前日比(値)","前日比(率)",
    "売買代金","PER","PBR","利回り"
]

options = Options()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

print("===== START =====")

saved_total = 0
rank = 1
empty_page_count = 0

with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(header)

    for page in range(1, MAX_PAGES + 1):

        url = BASE_URL.format(page)

        print(f"\n[PAGE] {page} / URL: {url}")

        driver.get(url)
        time.sleep(random.uniform(2, 4))

        rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

        print(f"[INFO] rows detected: {len(rows)}")

        if len(rows) == 0:
            empty_page_count += 1
            print(f"[WARN] empty page streak: {empty_page_count}")

            if empty_page_count >= 3:
                print("===== STOP: 連続空ページ =====")
                break
            continue

        empty_page_count = 0

        page_saved = 0

        for row in rows:

            text = row.text.strip().replace("\n", " ")

            # ノイズ除外
            if not text:
                continue
            if "プレミアム" in text:
                continue

            m = re.search(r"\b\d{4}[A-Z]?\b", text)
            if not m:
                continue

            code = m.group(0)

            try:
                parts = text.split()

                # 最低限の安全チェック
                if len(parts) < 6:
                    continue

                writer.writerow([
                    today,
                    rank,
                    code,
                    "",   # 銘柄名は簡略化（必要なら強化可）
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    "",
                    ""
                ])

                rank += 1
                page_saved += 1
                saved_total += 1

            except Exception as e:
                print("[ERROR]", e)
                continue

        print(f"[RESULT] page saved rows: {page_saved}")
        print(f"[TOTAL] saved so far: {saved_total}")

print("\n===== END =====")
print(f"file: {output_file}")

driver.quit()
