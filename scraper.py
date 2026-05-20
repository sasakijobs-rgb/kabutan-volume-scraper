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

print("===== START =====")
print(url)

# ==========================================
# Chrome設定
# ==========================================
options = Options()

# headlessなし
# options.add_argument("--headless")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

# bot検知回避
options.add_argument("--disable-blink-features=AutomationControlled")

# UserAgent
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

# automation表示削除
options.add_experimental_option(
    "excludeSwitches",
    ["enable-automation"]
)

options.add_experimental_option(
    "useAutomationExtension",
    False
)

# ==========================================
# driver起動
# ==========================================
print("===== Chrome 起動 =====")

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

print("===== Chrome 起動完了 =====")

try:

    # ==========================================
    # ページアクセス
    # ==========================================
    print("===== access =====")

    driver.get(url)

    sleep_sec = random.uniform(8, 12)

    print(f"sleep {sleep_sec:.2f} sec")

    time.sleep(sleep_sec)

    # ==========================================
    # TITLE確認
    # ==========================================
    print("\n===== TITLE =====")
    print(driver.title)

    # ==========================================
    # TABLE確認
    # ==========================================
    tables = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table.st_market"
    )

    print("\n===== table count =====")
    print(len(tables))

    # ==========================================
    # TR確認
    # ==========================================
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "table.stock_table.st_market tbody tr"
    )

    print("\n===== tr count =====")
    print(len(rows))

    # ==========================================
    # 1件取得
    # ==========================================
    if len(rows) > 0:

        print("\n===== first row raw =====")
        print(rows[0].text)

        row = rows[0]

        # ------------------------------
        # td一覧
        # ------------------------------
        tds = row.find_elements(By.TAG_NAME, "td")

        print("\n===== td count =====")
        print(len(tds))

        for i, td in enumerate(tds):

            print(f"td[{i}] = {td.text}")

        # ------------------------------
        # th一覧
        # ------------------------------
        ths = row.find_elements(By.TAG_NAME, "th")

        print("\n===== th count =====")
        print(len(ths))

        for i, th in enumerate(ths):

            print(f"th[{i}] = {th.text}")

        # ==========================================
        # 実データ取得
        # ==========================================
        code = tds[0].text.strip()

        name = ths[0].text.strip()

        market = tds[1].text.strip()

        price = tds[4].text.strip()

        prev_diff = tds[6].text.strip()

        prev_diff_percent = tds[7].text.strip()

        trading_value = tds[8].text.strip()

        per = tds[9].text.strip()

        pbr = tds[10].text.strip()

        yield_ = tds[11].text.strip()

        print("\n===== RESULT =====")

        print("コード =", code)
        print("銘柄名 =", name)
        print("市場 =", market)
        print("株価 =", price)
        print("前日比 =", prev_diff)
        print("前日比% =", prev_diff_percent)
        print("売買代金 =", trading_value)
        print("PER =", per)
        print("PBR =", pbr)
        print("利回り =", yield_)

    else:

        print("TRが取得できません")

    # ==========================================
    # screenshot
    # ==========================================
    driver.save_screenshot("debug.png")

    print("\n===== screenshot saved =====")

except Exception as e:

    print("\n===== ERROR =====")
    print(type(e))
    print(e)

finally:

    driver.quit()

    print("\n===== END =====")
