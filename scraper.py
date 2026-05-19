import os
import time
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

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
# Chrome Options（重要）
# =========================
options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--remote-debugging-port=9222")

options.add_argument(
    "--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)

options.add_argument("--disable-blink-features=AutomationControlled")

# =========================
# Chrome起動
# =========================
print("Chrome起動開始")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# webdriverフラグ無効化（軽いbot対策）
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

try:

    # =========================
    # ページアクセス
    # =========================
    print("ページアクセス開始")

    driver.get(url)

    time.sleep(5)

    print("ページタイトル:")
    print(driver.title)

    # =========================
    # tbody確認
    # =========================
    tbodies = driver.find_elements(By.TAG_NAME, "tbody")

    print("=" * 80)
    print("tbody数:", len(tbodies))

    all_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("全tr数:", len(all_rows))

    # =========================
    # ランキング行抽出
    # =========================
    rows = []

    for row in all_rows:
        if row.find_elements(By.TAG_NAME, "th"):
            rows.append(row)

    print("ランキング行数:", len(rows))

    # =========================
    # 1件デバッグ（重要）
    # =========================
    print("=" * 80)
    print("1件デバッグ開始")
    print("=" * 80)

    if rows:

        row = rows[0]

        print("\n■ outerHTML")
        print(row.get_attribute("outerHTML")[:1500])

        ths = row.find_elements(By.TAG_NAME, "th")
        tds = row.find_elements(By.TAG_NAME, "td")

        print("\n■ th数:", len(ths))
        print("■ td数:", len(tds))

        lines = []

        if ths:
            print("\n■ th.text")
            print(ths[0].text)

            lines = [
                x.strip()
                for x in ths[0].text.split("\n")
                if x.strip()
            ]

            print("\n■ th分解")
            for i, v in enumerate(lines):
                print(f"th[{i}] = {v}")

        for i, td in enumerate(tds):
            print(f"td[{i}] = {td.text}")

    # =========================
    # CSVデータ取得
    # =========================
    data = []

    for row in rows:

        try:

            ths = row.find_elements(By.TAG_NAME, "th")
            if not ths:
                continue

            lines = [
                x.strip()
                for x in ths[0].text.split("\n")
                if x.strip()
            ]

            code = lines[0] if len(lines) > 0 else ""
            name = lines[1] if len(lines) > 1 else ""
            market = lines[2] if len(lines) > 2 else ""

            tds = row.find_elements(By.TAG_NAME, "td")
            if len(tds) < 7:
                continue

            price = tds[0].text
            diff = tds[1].text
            value = tds[3].text
            per = tds[4].text
            pbr = tds[5].text
            dividend = tds[6].text

            data.append([
                code,
                name,
                market,
                price,
                diff,
                value,
                per,
                pbr,
                dividend
            ])

        except Exception as e:
            print("ERROR:", e)

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
            "売買代金",
            "PER",
            "PBR",
            "利回り"
        ])

        writer.writerows(data)

    print("=" * 80)
    print("CSV保存完了:", file_path)

finally:
    driver.quit()
    print("=" * 80)
    print("終了")
