import time
import random

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

print("===== START =====")
print("URL:", URL)

# =========================
# Chrome（安定優先）
# =========================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0 Chrome/120")

driver = webdriver.Chrome(options=options)

try:
    print("\n===== Chrome 起動 =====")

    driver.get(URL)

    time.sleep(random.uniform(3, 6))

    print("\n===== TITLE =====")
    print(driver.title)

    rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    print("\n===== ROW COUNT =====")
    print(len(rows))

    if not rows:
        print("❌ データ取得できません（WAF or セレクタ不一致）")
        driver.save_screenshot("debug.png")
        exit()

    row = rows[0]

    print("\n===== RAW ROW =====")
    print(row.text)

    # =========================
    # 銘柄（改行対応）
    # =========================
    th = row.find_element(By.TAG_NAME, "th")
    th_lines = [x.strip() for x in th.text.split("\n") if x.strip()]

    code = ""
    name = ""
    market = ""

    # div/p構造優先（安定）
    try:
        code = th.find_element(By.CSS_SELECTOR, "div").text.strip()
    except:
        pass

    try:
        name = th.find_element(By.CSS_SELECTOR, "p").text.strip()
    except:
        pass

    # fallback
    if not code or not name:
        if len(th_lines) >= 1:
            parts = th_lines[0].split()
            if len(parts) >= 2:
                code = parts[0]
                name = parts[1]

    if len(th_lines) >= 2:
        market = th_lines[1]

    # =========================
    # 数値データ
    # =========================
    tds = row.find_elements(By.TAG_NAME, "td")

    def safe(i):
        return tds[i].text.strip() if i < len(tds) else ""

    price = safe(0)
    prev = safe(1)
    trade_value = safe(3)
    per = safe(4)
    pbr = safe(5)
    yield_ = safe(6)

    # =========================
    # DISPLAY（ここがメイン）
    # =========================
    print("\n==============================")
    print("📊 取得データチェック（1件）")
    print("==============================")

    def show(label, value):
        status = "OK" if value else "NG"
        print(f"{label:<10}: {value} [{status}]")

    show("コード", code)
    show("銘柄名", name)
    show("市場", market)
    show("株価", price)
    show("前日比", prev)
    show("売買代金", trade_value)
    show("PER", per)
    show("PBR", pbr)
    show("利回り", yield_)

    print("\n==============================")

    # 参考：未取得チェックまとめ
    missing = []
    for k, v in {
        "コード": code,
        "銘柄名": name,
        "市場": market,
        "株価": price,
        "前日比": prev,
        "売買代金": trade_value,
        "PER": per,
        "PBR": pbr,
        "利回り": yield_,
    }.items():
        if not v:
            missing.append(k)

    if missing:
        print("⚠ 未取得項目:", missing)
    else:
        print("✅ 全項目取得OK")

    driver.save_screenshot("debug.png")
    print("\n===== screenshot saved =====")

except Exception as e:
    print("\n===== ERROR =====")
    print(type(e))
    print(e)

finally:
    driver.quit()
    print("\n===== END =====")
