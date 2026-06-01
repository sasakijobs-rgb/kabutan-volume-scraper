import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL = "https://shikiho.toyokeizai.net/market/N225"


def safe_text(driver, css):
    try:
        return driver.find_element(By.CSS_SELECTOR, css).text.strip()
    except:
        return ""


def fetch():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    # JS描画待ち（最小安定値）
    driver.implicitly_wait(10)

    # =========================
    # 基本値
    # =========================
    current = safe_text(driver, ".basic-section__price__current")
    change = safe_text(driver, ".basic-section__price__change")

    # =========================
    # dt/dd構造を辞書化
    # =========================
    data_map = {}

    for dt in driver.find_elements(By.CSS_SELECTOR, "dl dt"):
        try:
            key = dt.text.strip()
            value = dt.find_element(By.XPATH, "following-sibling::dd[1]").text.strip()
            data_map[key] = value
        except:
            continue

    driver.quit()

    # =========================
    # 日付・時間は固定（重要）
    # =========================
    now = datetime.now()
    date_str = now.strftime("%Y/%m/%d")
    time_str = "15:30"

    # =========================
    # 安全getter（型ズレ防止）
    # =========================
    def g(k):
        return data_map.get(k, "").replace("\n", " ").strip()

    row = {
        "日付": f"{date_str} {time_str}",
        "現在値": current,
        "前日比": change,
        "始値": g("始値"),
        "前日終値": g("前日終値"),
        "高値": g("高値"),
        "安値": g("安値"),
        "年初来高値": g("年初来高値"),
        "年初来安値": g("年初来安値"),
        "出来高": g("出来高"),
        "売買代金": g("売買代金"),
    }

    return row


def save(data):

    os.makedirs("output", exist_ok=True)

    path = "output/nikkei_avg_data.csv"
    exists = os.path.isfile(path)

    cols = list(data.keys())

    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        if not exists:
            w.writerow(cols)

        # ★None対策（絶対に落ちない）
        w.writerow([data.get(c, "") for c in cols])


def main():

    try:
        data = fetch()
        save(data)
        print("saved")

    except Exception as e:
        # ★ここで止めない（GitHub Actions安定化）
        print("error:", e)


if __name__ == "__main__":
    main()
