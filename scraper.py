from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

options = Options()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--user-agent=Mozilla/5.0")

driver = webdriver.Chrome(options=options)

driver.get(url)
time.sleep(2)

rows = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

data = []

for i, row in enumerate(rows[:15]):  # ← 15件だけ
    cols = row.find_elements(By.TAG_NAME, "td")

    if len(cols) < 4:
        continue

    code = cols[0].text.strip()
    name = cols[1].text.strip()
    price = cols[2].text.strip()
    value = cols[3].text.strip()

    data.append([code, name, price, value])

driver.quit()

for d in data:
    print(d)
