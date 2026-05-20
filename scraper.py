import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# ==========================================
# URL
# ==========================================
url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

print("===== 開始 =====")
print(url)

# ==========================================
# Chrome設定
# ==========================================
options = Options()

# headlessを使わない
# options.add_argument("--headless")

# bot判定回避
options.add_argument("--disable-blink-features=AutomationControlled")

# 通常ブラウザ風
options.add_argument("--start-maximized")

# Linux用
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# UserAgent
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# automation非表示
options.add_experimental_option(
    "excludeSwitches",
    ["enable-automation"]
)

options.add_experimental_option(
    "useAutomationExtension",
    False
)

print("===== Chrome起動 =====")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# webdriver隠蔽
driver.execute_script("""
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
})
""")

print("===== Chrome起動完了 =====")

try:

    # ==========================================
    # アクセス
    # ==========================================
    print("===== アクセス開始 =====")

    driver.get(url)

    print("===== アクセス完了 =====")

    # 人間っぽい待機
    sleep_sec = random.uniform(8, 12)

    print(f"===== sleep {sleep_sec:.2f} 秒 =====")

    time.sleep(sleep_sec)

    # ==========================================
    # 基本情報
    # ==========================================
    print("\n===== TITLE =====")
    print(driver.title)

    print("\n===== CURRENT URL =====")
    print(driver.current_url)

    # ==========================================
    # body確認
    # ==========================================
    print("\n===== BODY TEXT =====")

    body = driver.find_element(By.TAG_NAME, "body")

    body_text = body.text

    print(body_text[:2000])

    # ==========================================
    # HTML確認
    # ==========================================
    html = driver.page_source

    print("\n===== HTML文字数 =====")
    print(len(html))

    print("\n===== HTML先頭1000文字 =====")
    print(html[:1000])

    # ==========================================
    # table確認
    # ==========================================
    print("\n===== TABLE確認 =====")

    tables = driver.find_elements(By.TAG_NAME, "table")

    print("table数 =", len(tables))

    # ==========================================
    # stock_table確認
    # ==========================================
    stock_tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table"
    )

    print("stock_table数 =", len(stock_tables))

    # ==========================================
    # st_market確認
    # ==========================================
    market_tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.st_market"
    )

    print("st_market数 =", len(market_tables))

    # ==========================================
    # 両方確認
    # ==========================================
    full_tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table.st_market"
    )

    print("stock_table st_market数 =", len(full_tables))

    # ==========================================
    # tr確認
    # ==========================================
    trs = driver.find_elements(By.TAG_NAME, "tr")

    print("\ntr数 =", len(trs))

    # ==========================================
    # selector確認
    # ==========================================
    print("\n===== selector確認 =====")

    selectors = [
        "table tr",
        "tbody tr",
        "table.stock_table tr",
        "table.stock_table.st_market tr",
        ".stock_table tr",
        ".st_market tr"
    ]

    for selector in selectors:

        elems = driver.find_elements(
            By.CSS_SELECTOR,
            selector
        )

        print(selector, "=", len(elems))

    # ==========================================
    # 1件表示
    # ==========================================
    print("\n===== 最初のTR =====")

    if len(trs) > 0:

        print(trs[0].text)

    else:

        print("TRなし")

    # ==========================================
    # screenshot
    # ==========================================
    driver.save_screenshot("debug.png")

    print("\n===== screenshot保存 =====")
    print("debug.png")

except Exception as e:

    print("\n===== エラー =====")
    print(type(e))
    print(e)

finally:

    print("\n===== Chrome終了 =====")

    driver.quit()
