import time
import random
import csv
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait

# ==========================================
# 設定
# ==========================================
PAGE = 83

URL = (
    "https://kabutan.jp/warning/"
    "trading_value_ranking?market=0"
    "&capitalization=-1&dispmode=normal"
    "&stc=&stm=0&page={}"
).format(PAGE)

today = datetime.now().strftime("%Y%m%d")

output_file = f"output/page_{PAGE}_{today}.csv"

header = [
    "日付", "順位", "コード", "銘柄名", "市場",
    "株価", "前日比", "前日比率",
    "売買代金", "PER", "PBR", "利回り"
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
# コード判定
# ==========================================
def is_code(x):
    return re.fullmatch(r"[A-Z0-9]{4,5}", x.strip().upper())

try:

    print("===== START =====")
    print("URL:", URL)

    driver.get(URL)

    # ==========================================
    # ★重要：JS描画待ち（ここがポイント）
    # ==========================================
    WebDriverWait(driver, 15).until(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, "tbody tr")) > 0
    )

    time.sleep(2)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("rows:", len(rows))

    if len(rows) == 0:
        print("❌ データ取得失敗（JS未描画 or ブロック）")
        driver.save_screenshot("debug_83.png")
        exit()

    # ==========================================
    # CSV出力
    # ==========================================
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)
        writer.writerow(header)

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

    print("\n===== DONE =====")
    print("file:", output_file)

finally:
    driver.quit()
    print("===== END =====")
