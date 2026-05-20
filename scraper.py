import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# 設定
# =========================
BASE_URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page={}"

# 例:
# page=1
# page=2
# page=3
PAGE_NO = 1

# =========================
# Seleniumセットアップ
# =========================
options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0")

driver = None

try:
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    # =========================
    # ページ取得
    # =========================
    url = BASE_URL.format(PAGE_NO)

    print(f"取得URL: {url}")

    driver.get(url)

    time.sleep(3)

    # =========================
    # テーブル取得
    # table.stock_table.st_market
    # =========================
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table.st_market tbody tr"
    )

    if not rows:
        print("データが取得できませんでした")
        exit()

    # =========================
    # 1件のみ取得
    # =========================
    row = rows[0]

    # -------------------------
    # コード
    # -------------------------
    code = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(1)"
    ).text.strip()

    # -------------------------
    # 銘柄名
    # -------------------------
    name = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(2) a"
    ).text.strip()

    # -------------------------
    # 市場
    # -------------------------
    market = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(3)"
    ).text.strip()

    # -------------------------
    # 株価
    # -------------------------
    price = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(4)"
    ).text.strip()

    # -------------------------
    # 前日比
    # -------------------------
    prev_diff = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(5)"
    ).text.strip()

    # -------------------------
    # 売買代金
    # -------------------------
    trading_value = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(6)"
    ).text.strip()

    # -------------------------
    # PER
    # -------------------------
    per = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(7)"
    ).text.strip()

    # -------------------------
    # PBR
    # -------------------------
    pbr = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(8)"
    ).text.strip()

    # -------------------------
    # 利回り
    # -------------------------
    yield_ = row.find_element(
        By.CSS_SELECTOR,
        "td:nth-child(9)"
    ).text.strip()

    # =========================
    # 出力確認
    # =========================
    print(f"コード：{code}")
    print(f"銘柄名：{name}")
    print(f"市場：{market}")
    print(f"株価：{price}")
    print(f"前日比：{prev_diff}")
    print(f"売買代金：{trading_value}")
    print(f"PER：{per}")
    print(f"PBR：{pbr}")
    print(f"利回り：{yield_}")

    # =========================
    # CSV出力部分（今回はコメントアウト）
    # =========================
    """
    with open("output.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            code,
            name,
            market,
            price,
            prev_diff,
            trading_value,
            per,
            pbr,
            yield_
        ])
    """

    # =========================
    # merged結合部分（今回はコメントアウト）
    # =========================
    """
    import pandas as pd

    df1 = pd.read_csv("file1.csv")
    df2 = pd.read_csv("file2.csv")

    merged = pd.concat([df1, df2], ignore_index=True)
    merged.to_csv("merged.csv", index=False, encoding="utf-8")
    """

except Exception as e:
    print(f"エラー: {e}")

finally:
    if driver:
        driver.quit()
