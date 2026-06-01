import csv
import os
import time
from datetime import datetime
from re

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


URL = "https://shikiho.toyokeizai.net/market/N225"

def clean_value(v):
    if v is None:
        return ""

    v = str(v)

    # 数値のカンマ削除（1,234 → 1234）
    v = v.replace(",", "")

    # 全角スペース・余計な空白整理
    v = v.replace("\n", "").replace("\t", "").strip()

    return v
    
def get_text(driver, label):
    try:
        dts = driver.find_elements(By.CSS_SELECTOR, "dl dt")
        for dt in dts:
            if dt.text.strip() == label:
                dd = dt.find_element(By.XPATH, "following-sibling::dd[1]")
                return dd.text.strip()
        return ""
    except:
        return ""


def fetch():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".basic-section"))
    )

    time.sleep(2)

    now = datetime.now()

    data = {
        "日付": now.strftime("%Y/%m/%d"),
        "時間": "15:30",

        "現在値": driver.find_element(By.CSS_SELECTOR, ".basic-section__price__current").text.strip(),
        "前日比": driver.find_element(By.CSS_SELECTOR, ".basic-section__price__change").text.strip(),

        "始値": get_text(driver, "始値"),
        "高値": get_text(driver, "高値"),
        "安値": get_text(driver, "安値"),

        "年初来高値": get_text(driver, "年初来高値"),
        "年初来安値": get_text(driver, "年初来安値"),

        "出来高": get_text(driver, "出来高"),
        "売買代金": get_text(driver, "売買代金"),
        "└ 22日平均": get_text(driver, "└ 22日平均"),

        "年初来株価上昇率": get_text(driver, "年初来株価上昇率"),
        "200日移動平均乖離率": get_text(driver, "200日移動平均乖離率"),
    }

    driver.quit()
    return data


# =========================
# 全履歴（追記）
# =========================
def save_merged(data):

    os.makedirs("output", exist_ok=True)

    path = "output/nikkei_avg_data_merged.csv"
    exists = os.path.isfile(path)

    cols = list(data.keys())

    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        if not exists:
            w.writerow(cols)

        w.writerow([clean_value(data.get(c, "")) for c in cols])
        
# =========================
# 今日だけ（上書き）
# =========================
def save_today(data):

    path = "output/nikkei_avg_data.csv"

    cols = list(data.keys())

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        w.writerow(cols)
        w.writerow([clean_value(data.get(c, "")) for c in cols])

def main():
    try:
        data = fetch()

        save_merged(data)
        save_today(data)

        print("nikkei_abg_data_saved")

    except Exception as e:
        print("error:", e)


if __name__ == "__main__":
    main()
