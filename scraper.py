import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# =========================
# URL
# =========================
url = "https://s.kabutan.jp/warnings/trading_value_ranking?market=all&page=1"

print("\n===== START =====")
print("URL:", url)

# =========================
# Chrome設定（安定ルート）
# =========================
options = Options()

# headlessは外す（デバッグ優先）
# options.add_argument("--headless")

options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

options.add_argument("--disable-blink-features=AutomationControlled")

options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

print("\n===== Chrome 起動 =====")

driver = webdriver.Chrome(
    service=Service(ChromeDriverManager().install()),
    options=options
)

# webdriver検出回避（軽い対策）
driver.execute_script("""
Object.defineProperty(navigator, 'webdriver', {
    get: () => undefined
})
""")

print("===== Chrome 起動完了 =====")

try:
    # =========================
    # アクセス
    # =========================
    print("\n===== ACCESS =====")
    driver.get(url)

    sleep_sec = random.uniform(6, 10)
    print(f"sleep: {sleep_sec:.2f} sec")
    time.sleep(sleep_sec)

    # =========================
    # ページ情報
    # =========================
    print("\n===== PAGE INFO =====")
    print("TITLE:", driver.title)
    print("URL:", driver.current_url)

    # =========================
    # WAFチェック
    # =========================
    html = driver.page_source
    print("\n===== HTML SIZE =====")
    print(len(html))

    if "Human Verification" in html or "AWS WAF" in html:
        print("\n❌ WAF検知")
        print(html[:500])
        driver.save_screenshot("waf_error.png")
        driver.quit()
        exit()

    # =========================
    # ROW取得
    # =========================
    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("\n===== ROW COUNT =====")
    print(len(rows))

    if len(rows) == 0:
        print("❌ データなし")
        driver.save_screenshot("no_rows.png")
        driver.quit()
        exit()

    # =========================
    # 1行取得
    # =========================
    row = rows[0]

    print("\n===== FIRST ROW RAW TEXT =====")
    print(row.text)

    ths = row.find_elements(By.TAG_NAME, "th")
    tds = row.find_elements(By.TAG_NAME, "td")

    print("\n===== TH COUNT =====", len(ths))
    print("===== TD COUNT =====", len(tds))

    # =========================
    # 🔥 銘柄情報（改行対応）
    # =========================
    print("\n===== STOCK INFO PARSE =====")

    if ths:
        raw_text = ths[0].text.strip()
        print("RAW TH TEXT:")
        print(raw_text)

        raw_parts = raw_text.split("\n")

        code = raw_parts[0] if len(raw_parts) > 0 else ""
        market = raw_parts[1] if len(raw_parts) > 1 else ""

        name_elem = ths[0].find_elements(By.TAG_NAME, "a")
        name = name_elem[0].text.strip() if name_elem else ""

        print("\n--- parsed ---")
        print("code   :", code)
        print("market :", market)
        print("name   :", name)

    else:
        print("❌ thなし")

    # =========================
    # 株価系データ（安全取得）
    # =========================
    print("\n===== PRICE INFO =====")

    def safe_td(i):
        return tds[i].text.strip() if len(tds) > i else ""

    price = safe_td(0)
    prev = safe_td(1)
    volume = safe_td(2)
    per = safe_td(4)
    pbr = safe_td(5)
    yield_ = safe_td(6)

    print("price :", price)
    print("prev  :", prev)
    print("volume:", volume)
    print("per   :", per)
    print("pbr   :", pbr)
    print("yield :", yield_)

    # =========================
    # スクショ
    # =========================
    driver.save_screenshot("debug.png")
    print("\n===== screenshot saved =====")

finally:
    driver.quit()
    print("\n===== END =====")
