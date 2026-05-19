import os
import time
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# =========================
# 設定
# =========================
FOLDER = "output"
os.makedirs(FOLDER, exist_ok=True)

today = datetime.now().strftime("%Y%m%d")

file_path = os.path.join(
    FOLDER,
    f"trading_value_ranking_{today}.csv"
)

url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

# =========================
# Selenium設定
# =========================
options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

options.add_argument(
    "--user-agent=Mozilla/5.0"
)

# =========================
# Chrome起動
# =========================
print("Chrome起動")

driver = webdriver.Chrome(options=options)

# =========================
# ページ取得
# =========================
print("ページ取得開始")

driver.get(url)

time.sleep(5)

print("ページタイトル:", driver.title)

# =========================
# 行取得
# =========================
rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

print("取得行数:", len(rows))

data = []

# =========================
# データ取得
# =========================
for row in rows:

    try:

        # =========================
        # 銘柄名取得
        # =========================
        name_elem = row.find_elements(
            By.CSS_SELECTOR,
            "th a p, th a abbr"
        )

        if not name_elem:
            continue

        name = name_elem[0].text.strip()

        # =========================
        # コード・市場取得
        # =========================
        code = ""
        market = ""

        code_market = row.find_elements(
            By.CSS_SELECTOR,
            "th a div.flex"
        )

        if code_market:

            parts = code_market[0].text.split()

            if len(parts) >= 1:
                code = parts[0].strip()

            if len(parts) >= 2:
                market = parts[1].strip()

        # =========================
        # td取得
        # =========================
        tds = row.find_elements(By.TAG_NAME, "td")

        if len(tds) < 7:
            continue

        price = tds[0].text.strip()

        # 前日比
        diff_parts = tds[1].text.split("\n")

        diff = diff_parts[0].strip() if len(diff_parts) > 0 else ""
        diff_percent = diff_parts[1].strip() if len(diff_parts) > 1 else ""

        trading_value = tds[3].text.strip()
        per = tds[4].text.strip()
        pbr = tds[5].text.strip()
        dividend = tds[6].text.strip()

        print(
            code,
            name,
            market,
            price,
            diff,
            diff_percent,
            trading_value,
            per,
            pbr,
            dividend
        )

        # =========================
        # 保存
        # =========================
        data.append([
            code,
            name,
            market,
            price,
            diff,
            diff_percent,
            trading_value,
            per,
            pbr,
            dividend
        ])

        if len(data) >= 15:
            break

    except Exception as e:
        print("ERROR:", e)

# =========================
# ブラウザ終了
# =========================
driver.quit()

# =========================
# CSV保存
# =========================
with open(file_path, "w", newline="", encoding="utf-8-sig") as f:

    writer = csv.writer(f)

    writer.writerow([
        "コード",
        "銘柄名",
        "市場",
        "株価",
        "前日比",
        "前日比(%)",
        "売買代金",
        "PER",
        "PBR",
        "利回り"
    ])

    writer.writerows(data)

print(f"CSV保存完了: {file_path}")
