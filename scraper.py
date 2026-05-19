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
# Selenium設定（GitHub Actions対応）
# =========================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")
options.add_argument("--user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)

# =========================
# アクセス
# =========================
driver.get(url)
time.sleep(3)

rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

data = []

# =========================
# 15件取得
# =========================
for row in rows[:15]:
    cols = row.find_elements(By.TAG_NAME, "td")

    if len(cols) < 4:
        continue

    code = cols[0].text.strip()
    name = cols[1].text.strip()
    price = cols[2].text.strip()
    value = cols[3].text.strip()

    data.append([code, name, price, value])

driver.quit()

# =========================
# CSV出力
# =========================
with open(file_path, "w", encoding="utf-8") as f:
    f.write("コード,銘柄名,株価,売買代金\n")
    for d in data:
        f.write(",".join(d) + "\n")

print(f"完了: {file_path}")
