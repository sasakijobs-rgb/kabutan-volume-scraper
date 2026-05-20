import time
import random
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

URL = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=277"

options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1400,2200")

options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

try:
    print("アクセス:", URL)

    driver.get(URL)
    time.sleep(random.uniform(5, 8))

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("取得行数:", len(rows))

    if len(rows) == 0:
        print("⚠ データなし（空ページ or ブロックの可能性）")
    else:
        print("✔ データ取得成功")

        for i, row in enumerate(rows[:5]):
            print(f"\n--- row {i+1} ---")
            print(row.text.replace("\n", " | "))

finally:
    driver.quit()
    print("終了")
