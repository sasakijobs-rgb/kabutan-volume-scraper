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

# bot判定軽減
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
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

# JS描画待ち
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
        # th取得
        # =========================
        ths = row.find_elements(By.TAG_NAME, "th")

        # thが無い行はスキップ
        if not ths:
            continue

        th = ths[0]

        parts = th.text.split()

        # 初期化
        name = ""
        code = ""
        market = ""

        # =========================
        # データ解析
        # =========================
        if len(parts) >= 1:
            name = parts[0]

        if len(parts) >= 2:
            code = parts[1]

        if len(parts) >= 3:
            market = parts[2]

        # =========================
        # td取得
        # =========================
        tds = row.find_elements(By.TAG_NAME, "td")

        if len(tds) < 7:
            continue

        price = tds[0].text.strip()
        diff = tds[1].text.strip()
        diff_percent = tds[2].text.strip()
        trading_value = tds[3].text.strip()
        per = tds[4].text.strip()
        pbr = tds[5].text.strip()
        dividend = tds[6].text.strip()

        # デバッグ表示
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

        # データ保存
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

        # 15件だけ
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
with open(file_path, "w", newline="", encoding="utf-8") as f:

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
