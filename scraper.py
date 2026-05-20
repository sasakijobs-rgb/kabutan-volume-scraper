import time
import re
import csv
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# 設定
# ==========================================
URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=208"

today = datetime.now().strftime("%Y%m%d")
output_file = f"output/trading_value_page208_{today}.csv"

header = [
    "日付",
    "コード",
    "銘柄名",
    "市場",
    "株価",
    "前日比",
    "前日比率",
    "売買代金",
    "PER",
    "PBR",
    "利回り"
]

# ==========================================
# 判定関数（最重要）
# ==========================================
def is_stock_row(th_text: str) -> bool:
    """
    thのテキストから「銘柄行かどうか」を判定
    """
    lines = [x.strip() for x in th_text.split("\n") if x.strip()]

    if len(lines) < 2:
        return False

    code = lines[-1]  # 最後がコード

    return re.fullmatch(r"[0-9A-Z]{4,5}", code) is not None


# ==========================================
# Chrome設定
# ==========================================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1400,2200")

driver = webdriver.Chrome(options=options)

try:

    print("===== START =====")
    print("URL:", URL)

    driver.get(URL)

    time.sleep(5)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("rows:", len(rows))

    results = []

    # ==========================================
    # 解析ループ
    # ==========================================
    for row in rows:

        try:
            th = row.find_element(By.CSS_SELECTOR, "th")
            tds = row.find_elements(By.CSS_SELECTOR, "td")

            th_text = th.text.strip()

            # ★ここで完全フィルタ
            if not is_stock_row(th_text):
                continue

            lines = [x.strip() for x in th_text.split("\n") if x.strip()]

            name = lines[0]
            code = lines[-1]

            # tdが足りない行はスキップ
            if len(tds) < 7:
                continue

            price = tds[0].text.strip()
            prev_value = tds[1].text.strip()
            prev_rate = tds[2].text.strip()
            trading_value = tds[3].text.strip()
            per = tds[4].text.strip()
            pbr = tds[5].text.strip()
            yield_value = tds[6].text.strip()

            results.append([
                today,
                code,
                name,
                "",  # 市場（必要ならthから抽出可）
                price,
                prev_value,
                prev_rate,
                trading_value,
                per,
                pbr,
                yield_value
            ])

            print("OK:", code, name)

        except Exception as e:
            print("skip:", e)

    # ==========================================
    # CSV出力
    # ==========================================
    with open(output_file, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(results)

    print("\n===== DONE =====")
    print("rows saved:", len(results))
    print("file:", output_file)

finally:
    driver.quit()
    print("===== END =====")
