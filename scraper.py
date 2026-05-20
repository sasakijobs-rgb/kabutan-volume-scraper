import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By

# =========================
# URL
# =========================
url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

print("===== START =====")
print(url)

# =========================
# Chrome Options
# =========================
options = webdriver.ChromeOptions()

# GitHub Actionsでも安定する設定
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--lang=ja-JP")

# 重要：headless（Actionsでは必須）
options.add_argument("--headless=new")

# =========================
# driver起動（ここが改善ポイント）
# =========================
print("===== Chrome 起動 =====")

# webdriver-managerは使わない
driver = webdriver.Chrome(options=options)

print("===== Chrome 起動完了 =====")

try:
    print("===== access =====")
    driver.get(url)

    time.sleep(random.uniform(5, 8))

    print("\n===== TITLE =====")
    print(driver.title)

    print("\n===== URL =====")
    print(driver.current_url)

    # =========================
    # table確認
    # =========================
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table.st_market tbody tr"
    )

    print("\n===== row count =====")
    print(len(rows))

    if not rows:
        print("データ取得不可（WAF or ブロック）")
    else:
        row = rows[0]
        print("\n===== FIRST ROW =====")
        print(row.text)

        tds = row.find_elements(By.TAG_NAME, "td")
        ths = row.find_elements(By.TAG_NAME, "th")

        print("\n===== td count =====", len(tds))
        print("===== th count =====", len(ths))

        if len(tds) >= 10:
            print("\n===== PARSED RESULT =====")
            print("コード:", tds[0].text)
            print("銘柄名:", ths[0].text)
            print("市場:", tds[1].text)
            print("株価:", tds[4].text)
            print("前日比:", tds[6].text)
            print("売買代金:", tds[8].text)
            print("PER:", tds[9].text)
            print("PBR:", tds[10].text)
            print("利回り:", tds[11].text if len(tds) > 11 else "")

    print("\n===== END =====")

except Exception as e:
    print("\n===== ERROR =====")
    print(e)

finally:
    driver.quit()
