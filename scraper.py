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
BASE_URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page={}"

print("===== START =====")

# ==========================================
# 日付 & ファイル名
# ==========================================
today = datetime.now().strftime("%Y%m%d")
filename = f"output/trading_value_ranking_{today}.csv"

os.makedirs("output", exist_ok=True)

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
print("===== Chrome 起動 =====")
driver = webdriver.Chrome(options=options)

try:

    # ==========================================
    # CSV初期化
    # ==========================================
    with open(filename, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

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

        rank = 1

        # ==========================================
        # 2ページ取得
        # ==========================================
        for page in range(1, 3):

            url = BASE_URL.format(page)

            print("\n==============================")
            print("PAGE:", page)
            print(url)

            driver.get(url)

            time.sleep(random.uniform(5, 8))

            rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

            print("ROW:", len(rows))

            for row in rows:

                lines = row.text.split("\n")

                if len(lines) < 5:
                    continue

                name = lines[0].strip()
                code = lines[1].strip()
                market = lines[2].strip()

                price_prev = lines[3].strip()
                remain = lines[4].strip()

                # 株価 + 前日比
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

                # 表示
                print(f"[{rank}] {code} {name}")

                rank += 1

                # 30件制限
                if rank > 30:
                    break

            if rank > 30:
                break

    driver.save_screenshot("debug.png")

    print("\n===== 完了 =====")
    print("OUTPUT:", filename)

except Exception as e:
    print("\n===== ERROR =====")
    print(type(e))
    print(e)

finally:
    driver.quit()
    print("===== END =====")
