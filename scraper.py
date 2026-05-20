import os
import csv
import time
import random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import re

# ==========================================
# 設定
# ==========================================
BASE_URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={}"

PAGES_TO_CHECK = [1, 83]

today = datetime.now().strftime("%Y%m%d")

os.makedirs("output", exist_ok=True)

output_file = f"output/page_check_{today}.csv"

header = [
    "日付",
    "ページ",
    "順位",
    "コード",
    "銘柄名",
    "市場",
    "株価",
    "前日比",
    "前日比率",
    "売買代金",
    "PER",
    "PBR",
    "利回り"
]

# ==========================================
# Chrome
# ==========================================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1400,2200")

driver = webdriver.Chrome(options=options)

# ==========================================
# コード判定（英数字4〜5文字）
# ==========================================
def is_code(x):
    return re.fullmatch(r"[A-Z0-9]{4,5}", x.strip().upper())

try:
    print("===== START =====")

    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)

        for page in PAGES_TO_CHECK:

            url = BASE_URL.format(page)

            print("\nPAGE:", page, url)

            driver.get(url)
            time.sleep(random.uniform(2, 4))

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            print("rows:", len(rows))

            rank = 1

            for row in rows:

                txt = row.text.strip()
                if not txt:
                    continue

                lines = txt.split("\n")

                code_index = -1

                for i, line in enumerate(lines):
                    if is_code(line):
                        code_index = i
                        break

                if code_index == -1:
                    continue

                if len(lines) < code_index + 4:
                    continue

                name = lines[code_index - 1]
                code = lines[code_index].upper()
                market = lines[code_index + 1]
                price_prev = lines[code_index + 2]
                remain = lines[code_index + 3]

                m = re.match(r"(.+?)\s+([+-].+)", price_prev)

                if m:
                    price = m.group(1)
                    prev_value = m.group(2)
                else:
                    price = price_prev
                    prev_value = ""

                parts = remain.split()

                prev_rate = parts[0] if len(parts) > 0 else ""
                trading_value = parts[1] if len(parts) > 1 else ""
                per = parts[2] if len(parts) > 2 else ""
                pbr = parts[3] if len(parts) > 3 else ""
                yield_value = parts[4] if len(parts) > 4 else ""

                writer.writerow([
                    today,
                    page,
                    rank,
                    code,
                    name,
                    market,
                    price,
                    prev_value,
                    prev_rate,
                    trading_value,
                    per,
                    pbr,
                    yield_value
                ])

                rank += 1

            print(f"✔ page {page} done")

    print("\n===== DONE =====")
    print("file:", output_file)

finally:
    driver.quit()
    print("===== END =====")
