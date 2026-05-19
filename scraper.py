import os
import time
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# =========================
# 設定
# =========================
FOLDER = "output"
os.makedirs(FOLDER, exist_ok=True)

today = datetime.now().strftime("%Y%m%d")
file_path = os.path.join(FOLDER, f"trading_value_ranking_{today}.csv")

url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

# =========================
# Selenium設定
# =========================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

driver.get(url)
time.sleep(3)

rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

data = []

# =========================
# 15件取得
# =========================
for row in rows[:15]:

    try:
        # -------------------------
        # 銘柄情報（th）
        # -------------------------
        th = row.find_element(By.TAG_NAME, "th")
        th_text = th.text.split("\n")

        name = th_text[0].strip() if len(th_text) > 0 else ""
        code = ""
        market = ""

        if len(th_text) > 1:
            parts = th_text[1].split()
            if len(parts) >= 1:
                code = parts[0]
            if len(parts) >= 2:
                market = parts[1]

        # -------------------------
        # 数値データ（td）
        # -------------------------
        td = row.find_elements(By.TAG_NAME, "td")

        if len(td) < 7:
            continue

        price = td[0].text.strip()
        prev = td[1].text.strip()
        volume = td[2].text.strip()
        trade_value = td[3].text.strip()
        per = td[4].text.strip()
        pbr = td[5].text.strip()
        yield_ = td[6].text.strip()

        data.append([
            code,
            name,
            market,
            price,
            prev,
            volume,
            trade_value,
            per,
            pbr,
            yield_
        ])

    except Exception:
        continue

driver.quit()

# =========================
# CSV出力
# =========================
with open(file_path, "w", encoding="utf-8") as f:
    f.write("コード,銘柄名,市場,株価,前日比,売買代金,PER,PBR,利回り\n")

    for d in data:
        f.write(",".join(d) + "\n")

print(f"完了: {file_path}")
