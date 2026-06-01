import csv
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL = "https://shikiho.toyokeizai.net/market/N225"


def fetch():

    options = Options()
    options.add_argument("--headless=new")  # GitHub Actions対応
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)

    driver.get(URL)

    # JS描画待ち（重要）
    time.sleep(5)

    def get_text(css):
        try:
            return driver.find_element(By.CSS_SELECTOR, css).text
        except:
            return ""

    current = get_text(".basic-section__price__current")
    change = get_text(".basic-section__price__change")

    # dt/dd系
    labels = driver.find_elements(By.CSS_SELECTOR, "dl dt")

    data = {}

    for dt in labels:
        try:
            key = dt.text
            value = dt.find_element(By.XPATH, "following-sibling::dd[1]").text
            data[key] = value
        except:
            pass

    driver.quit()

    return [
        current,
        change,
        data.get("始値", ""),
        data.get("高値", ""),
        data.get("安値", ""),
        data.get("年初来高値", ""),
        data.get("年初来安値", ""),
    ]


def save(row):

    os.makedirs("output", exist_ok=True)

    path = "output/nikkei_avg_data.csv"
    exists = os.path.isfile(path)

    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        if not exists:
            w.writerow([
                "現在値",
                "前日比",
                "始値",
                "高値",
                "安値",
                "年初来高値",
                "年初来安値"
            ])

        w.writerow(row)


def main():

    row = fetch()
    save(row)

    print("saved")


if __name__ == "__main__":
    main()
