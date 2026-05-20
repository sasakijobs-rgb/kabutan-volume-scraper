import os
import re
import time
import random
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# 設定
# ==========================================
URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

TODAY = datetime.now().strftime("%Y%m%d")

print("===== START =====")
print("URL:", URL)

# ==========================================
# Chrome設定
# ==========================================
options = Options()

# GitHub Actions用
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# 軽量化
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1280,2000")

# UserAgent
options.add_argument(
    "--user-agent=Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# GitHub ActionsのChromeパス
options.binary_location = "/usr/bin/chromium-browser"

# ==========================================
# Chrome起動
# ==========================================
print("\n===== Chrome 起動 =====")

driver = webdriver.Chrome(options=options)

try:

    # ==========================================
    # アクセス
    # ==========================================
    driver.get(URL)

    sleep_sec = random.uniform(5, 8)

    print(f"sleep {sleep_sec:.2f} sec")

    time.sleep(sleep_sec)

    # ==========================================
    # TITLE
    # ==========================================
    print("\n===== TITLE =====")
    print(driver.title)

    # ==========================================
    # 行取得
    # ==========================================
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("\n===== ROW COUNT =====")
    print(len(rows))

    if len(rows) == 0:
        print("行取得失敗")
        driver.quit()
        exit()

    # ==========================================
    # 1件目
    # ==========================================
    rank = 1

    row = rows[0]

    print("\n===== RAW ROW =====")
    print(row.text)

    # ==========================================
    # 改行分割
    # ==========================================
    lines = row.text.split("\n")

    print("\n===== SPLIT DEBUG =====")

    for i, line in enumerate(lines):
        print(i, line)

    # ==========================================
    # 最低件数チェック
    # ==========================================
    if len(lines) < 9:
        print("\n❌ 想定より項目数が少ない")
        driver.save_screenshot("debug.png")
        driver.quit()
        exit()

    # ==========================================
    # パース
    # ==========================================
    name = lines[0].strip()

    code = lines[1].strip()

    market = lines[2].strip()

    # 51,290 +1,520
    price_prev = lines[3].strip()

    # +3.05%
    prev_rate = lines[4].strip()

    # 1,588,513
    trading_value = lines[5].strip()

    # ー倍
    per = lines[6].strip()

    # 20.0倍
    pbr = lines[7].strip()

    # ー%
    yield_value = lines[8].strip()

    # ==========================================
    # 株価 / 前日比(値)
    # ==========================================
    m = re.match(r"(.+?)\s+([+-].+)", price_prev)

    if m:
        price = m.group(1).strip()
        prev_value = m.group(2).strip()
    else:
        price = price_prev
        prev_value = ""

    # ==========================================
    # カンマ除去
    # ==========================================
    price = price.replace(",", "")
    prev_value = prev_value.replace(",", "")
    trading_value = trading_value.replace(",", "")

    # ==========================================
    # 表示
    # ==========================================
    print("\n==============================")
    print("📊 取得データチェック")
    print("==============================")

    print(f"0 日付        : {TODAY}")
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
    # CSV用データ
    # ==========================================
    record = [
        TODAY,
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
    # 出力部分（あとで有効化）
    # ==========================================
    #
    # os.makedirs("output", exist_ok=True)
    #
    # csv_path = f"output/trading_value_{TODAY}.csv"
    #
    # with open(csv_path, "a", encoding="utf-8-sig") as f:
    #     f.write(",".join(map(str, record)) + "\n")
    #

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
