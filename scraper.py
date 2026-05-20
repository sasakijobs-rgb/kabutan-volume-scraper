import os
import re
import time
import random
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# URL
# ==========================================
URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

print("===== START =====")
print("URL:", URL)

# ==========================================
# 日付
# ==========================================
today = datetime.now().strftime("%Y%m%d")

# ==========================================
# CSV出力ファイル
# ==========================================
os.makedirs("output", exist_ok=True)
csv_path = "output/first_page15_before.csv"

# ==========================================
# Chrome設定
# ==========================================
options = Options()

options.add_argument("--headless=new")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("--remote-debugging-port=9222")

options.add_argument("--window-size=1400,2200")

options.add_argument(
    "--user-agent=Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

options.binary_location = "/usr/bin/chromium-browser"

# ==========================================
# Chrome起動
# ==========================================
print("\n===== Chrome 起動 =====")
driver = webdriver.Chrome(options=options)

try:

    driver.get(URL)

    sleep_sec = random.uniform(5, 8)
    print(f"sleep {sleep_sec:.2f} sec")
    time.sleep(sleep_sec)

    print("\n===== TITLE =====")
    print(driver.title)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("\n===== ROW COUNT =====")
    print(len(rows))

    if len(rows) == 0:
        print("❌ row取得失敗")
        driver.save_screenshot("debug.png")
        exit()

    # ==========================================
    # 1件目
    # ==========================================
    rank = 1
    row = rows[0]

    print("\n===== RAW ROW =====")
    print(row.text)

    lines = row.text.split("\n")

    print("\n===== SPLIT DEBUG =====")
    for i, line in enumerate(lines):
        print(i, line)

    name = lines[0].strip()
    code = lines[1].strip()
    market = lines[2].strip()

    price_prev = lines[3].strip()
    remain = lines[4].strip()

    # 株価 / 前日比
    m = re.match(r"(.+?)\s+([+-].+)", price_prev)

    if m:
        price = m.group(1).strip()
        prev_value = m.group(2).strip()
    else:
        price = price_prev
        prev_value = ""

    remain_parts = remain.split()

    prev_rate = remain_parts[0] if len(remain_parts) > 0 else ""
    trading_value = remain_parts[1] if len(remain_parts) > 1 else ""
    per = remain_parts[2] if len(remain_parts) > 2 else ""
    pbr = remain_parts[3] if len(remain_parts) > 3 else ""
    yield_value = remain_parts[4] if len(remain_parts) > 4 else ""

    # カンマ除去
    price = price.replace(",", "")
    prev_value = prev_value.replace(",", "")
    trading_value = trading_value.replace(",", "")

    # ==========================================
    # 表示
    # ==========================================
    print("\n==============================")
    print("📊 取得データチェック")
    print("==============================")

    print(f"0 日付        : {today}")
    print(f"1 順位        : {rank}")
    print(f"2 コード      : {code}")
    print(f"3 銘柄名      : {name}")
    print(f"4 市場        : {market}")
    print(f"5 株価        : {price}")
    print(f"6 前日比(値)  : {prev_value}")
    print(f"7 前日比(率)  : {prev_rate}")
    print(f"8 売買代金    : {trading_value}")
    print(f"9 PER         : {per}")
    print(f"10 PBR        : {pbr}")
    print(f"11 利回り      : {yield_value}")

    # ==========================================
    # CSVレコード
    # ==========================================
    record = [
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
    ]

    print("\n===== CSV RECORD =====")
    print(record)

    # ==========================================
    # CSV出力（追加部分）
    # ==========================================
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)

        # ヘッダー（初回のみ）
        if not file_exists:
            writer.writerow([
                "日付",
                "順位",
                "コード",
                "銘柄名",
                "市場",
                "株価",
                "前日比(値)",
                "前日比(率)",
                "売買代金",
                "PER",
                "PBR",
                "利回り"
            ])

        writer.writerow(record)

    # ==========================================
    # screenshot
    # ==========================================
    driver.save_screenshot("debug.png")

    print("\n===== screenshot saved =====")

except Exception as e:

    print("\n===== ERROR =====")
    print(type(e))
    print(e)

finally:
    driver.quit()
    print("\n===== END =====")
