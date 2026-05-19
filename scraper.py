import os
import time
import random
import csv
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# 設定
# =========================
URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

# =========================
# ログ
# =========================
def log(msg):
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {msg}")

# =========================
# Selenium設定
# =========================
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

log("【取得開始】")

try:
    driver.get(URL)
    time.sleep(2 + random.random())

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    if not rows:
        log("データが取得できません")
        raise SystemExit

    # =========================
    # ★ 1件のみ取得
    # =========================
    row = rows[0]

    # 銘柄名
    name_elem = row.find_elements(By.CSS_SELECTOR, "th a p, th a abbr")
    name = name_elem[0].text.strip() if name_elem else ""

    # コード・市場
    code, market = "", ""
    code_market = row.find_elements(By.CSS_SELECTOR, "th a div.flex")
    if code_market:
        parts = code_market[0].text.split()
        if len(parts) >= 1:
            code = parts[0].strip()
        if len(parts) >= 2:
            market = parts[1].strip()

    # TD取得
    tds = row.find_elements(By.TAG_NAME, "td")
    if len(tds) < 7:
        log("列不足のため終了")
        raise SystemExit

    price = tds[0].text.strip()

    prev_text = tds[1].text.split("\n")
    prev_diff = prev_text[0].strip() if len(prev_text) > 0 else ""
    prev_diff_percent = prev_text[1].replace("%", "").strip() if len(prev_text) > 1 else ""

    volume = tds[2].text.replace("株", "").replace(",", "").strip()
    per = tds[4].text.replace("倍", "").strip()
    pbr = tds[5].text.replace("倍", "").strip()
    yield_ = tds[6].text.replace("%", "").strip()

    try:
        trade_amount = int(float(price.replace(",", "")) * float(volume))
    except:
        trade_amount = 0

    # =========================
    # ★ Display（確認表示）
    # =========================
    print("\n==============================")
    print("DISPLAY: 取得データ確認（1件）")
    print("==============================")

    print(f"コード            : {code}")
    print(f"銘柄名            : {name}")
    print(f"市場              : {market}")
    print(f"株価              : {price}")
    print(f"前日比            : {prev_diff}")
    print(f"前日比(%)         : {prev_diff_percent}")
    print(f"出来高            : {volume}")
    print(f"PER               : {per}")
    print(f"PBR               : {pbr}")
    print(f"利回り            : {yield_}")
    print(f"売買代金(概算)    : {trade_amount}")

    print("==============================\n")

    # =========================
    # ※DB投入イメージ（未実装）
    # stock_table st_market にINSERT可能
    # =========================
    log("stock_table st_market 用データ取得完了（未保存）")

finally:
    driver.quit()
    log("ブラウザ終了")
    log("【取得終了】")
