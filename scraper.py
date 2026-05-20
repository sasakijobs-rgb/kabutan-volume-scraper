from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=277"

# ==========================================
# Chrome
# ==========================================
options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1400,2200")

options.add_argument(
    "--user-agent=Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

try:

    print("アクセス:", URL)

    driver.get(URL)

    time.sleep(5)

    # ==========================================
    # tbody tr
    # ==========================================
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("rows:", len(rows))

    if len(rows) == 0:
        print("❌ rows取得失敗")
        exit()

    # ==========================================
    # 1件だけテスト
    # ==========================================
    row = rows[0]

    print("\n===== row.text =====")
    print(row.text)

    cells = row.find_elements(By.CSS_SELECTOR, "td, th")

    print("\n===== CELLS =====")

    values = []

    for i, c in enumerate(cells):

        txt = c.text.strip()

        print(i, txt)

        if txt == "":
            continue

        values.append(txt)

    print("\n===== FILTERED =====")
    print(values)

    # ==========================================
    # s.kabutan.jp はシンプル構造
    # ==========================================
    # 例:
    #
    # ['共同紙', '9849', '東Ｓ',
    #  '4,470 +5', '+0.11% 1 46.5 0.76 1.12']
    #
    # ==========================================

    if len(values) < 5:
        print("❌ 列不足")
        exit()

    name = values[0]
    code = values[1]
    market = values[2]

    price_prev = values[3]
    remain = values[4]

    # ==========================================
    # 株価 / 前日比
    # ==========================================
    import re

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

    print("\n===== RESULT =====")

    print("code         :", code)
    print("name         :", name)
    print("market       :", market)
    print("price        :", price)
    print("prev_value   :", prev_value)
    print("prev_rate    :", prev_rate)
    print("trading_value:", trading_value)
    print("per          :", per)
    print("pbr          :", pbr)
    print("yield        :", yield_value)

finally:

    driver.quit()

    print("\n終了")
