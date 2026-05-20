import re
import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=208"
DATE = "20260520"
OUTPUT = "trading_value_ranking_20260520.csv"

MARKET_PATTERN = r"^(東S|東P|名M|東E|東G)$"
CODE_PATTERN = r"^[0-9A-Z]{4,5}$"

HEADER = [
    "日付","No","コード","銘柄名","市場",
    "株価(百万円)","前日比","前日比(%)",
    "売買代金","PER","PBR","利回り"
]

def init_csv():
    with open(OUTPUT, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)

def create_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    return webdriver.Chrome(options=options)

# =========================
# データ抽出（ここが核心）
# =========================
def extract_rows(driver):
    driver.get(URL)
    time.sleep(3)

    text = driver.find_element(By.TAG_NAME, "body").text
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    rows = []

    i = 0
    while i < len(lines) - 10:
        line = lines[i]

        # 銘柄名っぽい行スキップ
        if "件 /" in line or "前へ" in line or "次へ" in line:
            i += 1
            continue

        # コード判定
        if re.match(CODE_PATTERN, line):
            code = line

            # 次行が市場コードか確認
            if i + 1 < len(lines) and re.match(MARKET_PATTERN, lines[i + 1]):

                market = lines[i + 1]

                # 銘柄名はその1つ前
                name = lines[i - 1] if i > 0 else ""

                # 数値群
                # ここは固定順で吸収
                try:
                    price_line = lines[i + 2].split()
                    price = price_line[0]
                    diff = price_line[1] if len(price_line) > 1 else ""

                    diff_pct = lines[i + 3]
                    volume = lines[i + 4]
                    per = lines[i + 5]
                    pbr = lines[i + 6]
                    yield_ = lines[i + 7]

                    rows.append([
                        DATE,
                        len(rows) + 4141,
                        code,
                        name,
                        market,
                        price,
                        diff,
                        diff_pct,
                        volume,
                        per,
                        pbr,
                        yield_
                    ])

                except:
                    pass

                i += 8
                continue

        i += 1

    return rows

def main():
    print("===== START =====")

    init_csv()

    driver = create_driver()

    try:
        rows = extract_rows(driver)

        print("[RESULT] rows:", len(rows))

        with open(OUTPUT, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerows(rows)

    finally:
        driver.quit()

    print("===== END =====")


if __name__ == "__main__":
    main()
