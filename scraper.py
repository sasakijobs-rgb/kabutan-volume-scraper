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

PAGE_NO = 1

# =========================
# Chrome設定
# =========================
options = Options()

# headless は新方式推奨
options.add_argument("--headless=new")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# UserAgent
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

driver = None

try:

    print("===== Chrome 起動開始 =====")

    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

    print("===== Chrome 起動成功 =====")

    # =========================
    # URL生成
    # =========================
    url = BASE_URL.format(PAGE_NO)

    print("===== アクセスURL =====")
    print(url)

    # =========================
    # ページ取得
    # =========================
    driver.get(url)

    print("===== driver.get 完了 =====")

    # 待機
    time.sleep(8)

    # =========================
    # 基本情報
    # =========================
    print("\n===== 基本情報 =====")

    print("TITLE:")
    print(driver.title)

    print("\nCURRENT URL:")
    print(driver.current_url)

    # =========================
    # HTML取得
    # =========================
    html = driver.page_source

    print("\n===== HTML情報 =====")

    print("HTML文字数:")
    print(len(html))

    print("\nHTML先頭2000文字:")
    print(html[:2000])

    # =========================
    # table確認
    # =========================
    print("\n===== TABLE確認 =====")

    tables = driver.find_elements(By.TAG_NAME, "table")

    print("table数:")
    print(len(tables))

    # stock_table確認
    stock_tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table"
    )

    print("\nstock_table数:")
    print(len(stock_tables))

    # st_market確認
    market_tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.st_market"
    )

    print("\nst_market数:")
    print(len(market_tables))

    # 両方
    full_tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table.st_market"
    )

    print("\nstock_table st_market数:")
    print(len(full_tables))

    # =========================
    # tr確認
    # =========================
    print("\n===== TR確認 =====")

    trs = driver.find_elements(By.TAG_NAME, "tr")

    print("tr数:")
    print(len(trs))

    # =========================
    # selector別確認
    # =========================
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

        try:
            elems = driver.find_elements(
                By.CSS_SELECTOR,
                selector
            )

            print(f"{selector} => {len(elems)} 件")

        except Exception as e:
            print(f"{selector} => ERROR")
            print(e)

    # =========================
    # 最初のtr表示
    # =========================
    print("\n===== 最初のTR =====")

    if len(trs) > 0:

        try:
            print(trs[0].text)

        except Exception as e:
            print(e)

    # =========================
    # body確認
    # =========================
    print("\n===== BODY確認 =====")

    try:
        body = driver.find_element(By.TAG_NAME, "body")

        body_text = body.text

        print(body_text[:3000])

    except Exception as e:
        print(e)

    # =========================
    # スクリーンショット
    # =========================
    screenshot_file = "debug.png"

    driver.save_screenshot(screenshot_file)

    print("\n===== スクリーンショット保存 =====")
    print(screenshot_file)

    print("\n===== 終了 =====")

except Exception as e:

    print("\n===== エラー発生 =====")
    print(type(e))
    print(e)

finally:

    if driver:

        driver.quit()

        print("\n===== Chrome終了 =====")
