import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# =========================
# URL
# =========================
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

print("Chrome起動開始")

driver = webdriver.Chrome(options=options)

print("ページアクセス開始")

driver.get(url)

# JS描画待ち
time.sleep(5)

print("ページタイトル:")
print(driver.title)

print("=" * 50)

# =========================
# HTML先頭確認
# =========================
html = driver.page_source

print("HTML先頭1000文字")
print(html[:1000])

print("=" * 50)

# =========================
# tbody確認
# =========================
tbodies = driver.find_elements(By.TAG_NAME, "tbody")

print("tbody数:", len(tbodies))

print("=" * 50)

# =========================
# tr確認
# =========================
rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

print("tr数:", len(rows))

print("=" * 50)

# =========================
# 1行目確認
# =========================
if len(rows) > 0:

    first_row = rows[0]

    print("1行目テキスト:")
    print(first_row.text)

    print("=" * 50)

    # td確認
    tds = first_row.find_elements(By.TAG_NAME, "td")

    print("td数:", len(tds))

    for i, td in enumerate(tds):
        print(f"td[{i}] = {td.text}")

    print("=" * 50)

    # th確認
    ths = first_row.find_elements(By.TAG_NAME, "th")

    print("th数:", len(ths))

    for i, th in enumerate(ths):
        print(f"th[{i}] = {th.text}")

else:
    print("rowsが0件です")

print("=" * 50)

print("終了")

driver.quit()
