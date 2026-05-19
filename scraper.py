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
print("Chrome起動開始")

driver = webdriver.Chrome(options=options)

try:

    # =========================
    # ページ取得
    # =========================
    print("ページアクセス開始")

    driver.get(url)

    time.sleep(5)

    print("ページタイトル:")
    print(driver.title)

    # =========================
    # HTML確認
    # =========================
    print("=" * 50)
    print("HTML先頭1000文字")

    html = driver.page_source

    print(html[:1000])

    # =========================
    # tbody確認
    # =========================
    print("=" * 50)

    tbodies = driver.find_elements(By.TAG_NAME, "tbody")

    print("tbody数:", len(tbodies))

    # =========================
    # 全行取得
    # =========================
    all_rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("=" * 50)
    print("全tr数:", len(all_rows))

    # =========================
    # ランキング行のみ抽出
    # =========================
    rows = []

    for row in all_rows:

        ths = row.find_elements(By.TAG_NAME, "th")

        # thがある行だけ
        if ths:
            rows.append(row)

    print("=" * 50)
    print("ランキング行数:", len(rows))

    # =========================
    # デバッグ表示
    # =========================
    for i, row in enumerate(rows[:3]):

        print("=" * 50)
        print(f"ランキング row[{i}] text")

        print(row.text)

        print("-" * 30)

        ths = row.find_elements(By.TAG_NAME, "th")
        tds = row.find_elements(By.TAG_NAME, "td")

        print("th数:", len(ths))
        print("td数:", len(tds))

        for j, th in enumerate(ths):
            print(f"th[{j}] = [{th.text}]")

        for j, td in enumerate(tds):
            print(f"td[{j}] = [{td.text}]")

    # =========================
    # データ取得
    # =========================
    data = []

    for row in rows:

        try:

            # =========================
            # th取得
            # =========================
            ths = row.find_elements(By.TAG_NAME, "th")

            if not ths:
                continue

            th = ths[0]

            # 改行維持
            lines = [
                x.strip()
                for x in th.text.split("\n")
                if x.strip()
            ]

            print("=" * 50)
            print("th lines:")
            print(lines)

            # =========================
            # コード・銘柄名・市場
            # =========================
            code = ""
            name = ""
            market = ""

            # 想定:
            # ['285A', 'キオクシア', '東Ｐ']

            if len(lines) >= 1:
                code = lines[0]

            if len(lines) >= 2:
                name = lines[1]

            if len(lines) >= 3:
                market = lines[2]

            # =========================
            # td取得
            # =========================
            tds = row.find_elements(By.TAG_NAME, "td")

            if len(tds) < 7:
                continue

            price = tds[0].text.strip()

            # 前日比
            diff_lines = [
                x.strip()
                for x in tds[1].text.split("\n")
                if x.strip()
            ]

            diff = ""
            diff_percent = ""

            if len(diff_lines) >= 1:
                diff = diff_lines[0]

            if len(diff_lines) >= 2:
                diff_percent = diff_lines[1]

            trading_value = tds[3].text.strip()
            per = tds[4].text.strip()
            pbr = tds[5].text.strip()
            dividend = tds[6].text.strip()

            # =========================
            # 表示
            # =========================
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

        except Exception as e:
            print("ERROR:", e)

    # =========================
    # CSV保存
    # =========================
    with open(
        file_path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

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

    print("=" * 50)
    print(f"CSV保存完了: {file_path}")

finally:

    # =========================
    # 終了
    # =========================
    driver.quit()

    print("=" * 50)
    print("終了")
