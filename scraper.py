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
# CSV出力
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
# 起動
# ==========================================
print("\n===== Chrome 起動 =====")
driver = webdriver.Chrome(options=options)

try:

    driver.get(URL)

    time.sleep(random.uniform(5, 8))

    print("\n===== TITLE =====")
    print(driver.title)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("\n===== ROW COUNT =====")
    print(len(rows))

    if len(rows) == 0:
        print("❌ 取得失敗")
        driver.save_screenshot("debug.png")
        exit()

    # ==========================================
    # CSV準備
    # ==========================================
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # ヘッダー（修正済み）
        writer.writerow([
            "日付",
            "順位",
            "コード",
            "銘柄名",
            "市場",
            "株価(百万円)",
            "前日比(値)",
            "前日比(率)",
            "売買代金",
            "PER",
            "PBR",
            "利回り"
        ])

        # ==========================================
        # 1ページ分ループ
        # ==========================================
        for rank, row in enumerate(rows[:15], start=1):

            lines = row.text.split("\n")

            if len(lines) < 5:
                continue

            name = lines[0].strip()
            code = lines[1].strip()
            market = lines[2].strip()

            price_prev = lines[3].strip()
            remain = lines[4].strip()

            # 株価と前日比
            m = re.match(r"(.+?)\s+([+-].+)", price_prev)
            if m:
                price = m.group(1).strip()
                prev_value = m.group(2).strip()
            else:
                price = price_prev
                prev_value = ""

            parts = remain.split()

            prev_rate = parts[0] if len(parts) > 0 else ""
            trading_value = parts[1] if len(parts) > 1 else ""
            per = parts[2] if len(parts) > 2 else ""
            pbr = parts[3] if len(parts) > 3 else ""
            yield_value = parts[4] if len(parts) > 4 else ""

            # カンマ除去
            price = price.replace(",", "")
            prev_value = prev_value.replace(",", "")
            trading_value = trading_value.replace(",", "")

            # ==========================================
            # 表示
            # ==========================================
            print("\n==============================")
            print(f"📊 {rank}件目")
            print("==============================")
            print("コード:", code)
            print("銘柄名:", name)
            print("市場:", market)
            print("株価:", price)
            print("前日比:", prev_value)
            print("前日比率:", prev_rate)
            print("売買代金:", trading_value)
            print("PER:", per)
            print("PBR:", pbr)
            print("利回り:", yield_value)

            # CSV書き込み
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

    driver.save_screenshot("debug.png")

    print("\n===== 完了 =====")

except Exception as e:
    print("\n===== ERROR =====")
    print(type(e))
    print(e)

finally:
    driver.quit()
    print("\n===== END =====")
