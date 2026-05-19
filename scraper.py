import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# =========================
# 設定
# =========================
url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

# =========================
# Selenium設定
# =========================
options = Options()

# ⚠ まずはheadlessをOFF（重要）
# options.add_argument("--headless=new")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

options.add_argument("--disable-blink-features=AutomationControlled")

# =========================
# 起動
# =========================
print("Chrome起動開始")

driver = webdriver.Chrome(options=options)

# bot検知回避（軽い対策）
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

try:

    print("ページアクセス開始")
    driver.get(url)

    time.sleep(5)

    print("ページタイトル:")
    print(driver.title)

    # =========================
    # まず全tbody確認
    # =========================
    tbodies = driver.find_elements(By.TAG_NAME, "tbody")

    print("=" * 80)
    print("tbody数:", len(tbodies))

    all_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("全tr数:", len(all_rows))

    # =========================
    # ランキング行だけ抽出（thがあるもの）
    # =========================
    rows = []

    for row in all_rows:

        ths = row.find_elements(By.TAG_NAME, "th")

        if ths:
            rows.append(row)

    print("ランキング行数:", len(rows))

    # =========================
    # ★ ここが本題：1件完全デバッグ
    # =========================
    print("=" * 80)
    print("1件デバッグ開始（完全解析）")
    print("=" * 80)

    for i, row in enumerate(rows[:1]):

        print(f"\n【ROW {i}】")
        print("-" * 80)

        # =========================
        # 生HTML
        # =========================
        print("■ outerHTML（先頭2000文字）")
        print(row.get_attribute("outerHTML")[:2000])

        # =========================
        # th確認
        # =========================
        ths = row.find_elements(By.TAG_NAME, "th")

        print("\n■ th数:", len(ths))

        lines = []

        if ths:

            print("\n■ th.text（生）")
            print(ths[0].text)

            lines = [
                x.strip()
                for x in ths[0].text.split("\n")
                if x.strip()
            ]

            print("\n■ th分解結果")
            for j, v in enumerate(lines):
                print(f"  th[{j}] = {v}")

        # =========================
        # td確認
        # =========================
        tds = row.find_elements(By.TAG_NAME, "td")

        print("\n■ td数:", len(tds))

        for j, td in enumerate(tds):
            print(f"td[{j}] = {td.text}")

        # =========================
        # 解析結果（最終）
        # =========================
        print("\n■ 最終パース結果")

        code = lines[0] if len(lines) > 0 else ""
        name = lines[1] if len(lines) > 1 else ""
        market = lines[2] if len(lines) > 2 else ""

        price = tds[0].text if len(tds) > 0 else ""
        diff = tds[1].text if len(tds) > 1 else ""
        value = tds[3].text if len(tds) > 3 else ""

        print("code   :", code)
        print("name   :", name)
        print("market :", market)
        print("price  :", price)
        print("diff   :", diff)
        print("value  :", value)

    print("=" * 80)
    print("終了")

finally:
    driver.quit()
