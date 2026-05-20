import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# =========================
# URL
# =========================
URL = "https://s.kabutan.jp/warnings/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&page=1"

print("===== START =====")
print("URL:", URL)

# =========================
# Chrome設定（軽量Chromium用）
# =========================
options = Options()

# GitHub Actions安定設定
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")

# bot検知軽減（最低限）
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/120.0.0.0 Safari/537.36"
)

print("===== Chrome 起動 =====")

driver = webdriver.Chrome(options=options)

try:
    # =========================
    # アクセス
    # =========================
    driver.get(URL)

    sleep_sec = random.uniform(5, 8)
    print(f"sleep {sleep_sec:.2f} sec")
    time.sleep(sleep_sec)

    # =========================
    # タイトル確認
    # =========================
    print("\n===== TITLE =====")
    print(driver.title)

    # =========================
    # テーブル取得
    # =========================
    rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")

    print("\n===== ROW COUNT =====")
    print(len(rows))

    if not rows:
        print("❌ データ取得できません（WAF or selector変更の可能性）")
        driver.save_screenshot("debug.png")
        exit()

    # =========================
    # 1件取得
    # =========================
    row = rows[0]

    print("\n===== RAW ROW =====")
    print(row.text)

    # th（銘柄情報）
    th = row.find_elements(By.TAG_NAME, "th")
    tds = row.find_elements(By.TAG_NAME, "td")

    print("\n===== PARSE =====")

    # 銘柄名（改行対応）
    if th:
        name = th[0].text.replace("\n", " ").strip()
        print("銘柄名:", name)

    # コード・市場（改行されているケース対応）
    try:
        code_market = th[0].text.split("\n")
        code = code_market[0].strip() if len(code_market) > 0 else ""
        market = code_market[1].strip() if len(code_market) > 1 else ""
        print("コード:", code)
        print("市場:", market)
    except:
        pass

    # 数値系
    for i, td in enumerate(tds):
        print(f"td[{i}]: {td.text}")

    # =========================
    # サンプル抽出（壊れない範囲）
    # =========================
    if len(tds) >= 5:
        price = tds[0].text
        change = tds[1].text
        volume = tds[2].text

        print("\n===== SAMPLE =====")
        print("株価:", price)
        print("前日比:", change)
        print("出来高:", volume)

    # =========================
    # スクショ
    # =========================
    driver.save_screenshot("debug.png")
    print("\n===== screenshot saved =====")

except Exception as e:
    print("\n===== ERROR =====")
    print(type(e))
    print(e)
    driver.save_screenshot("error.png")

finally:
    driver.quit()
    print("\n===== END =====")
