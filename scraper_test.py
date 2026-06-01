import csv
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


URL = "https://shikiho.toyokeizai.net/market/N225"


def get(driver, label):
    try:
        for dt in driver.find_elements(By.CSS_SELECTOR, "dl dt"):
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

    driver = webdriver.Chrome(options=options)
    driver.get(URL)

    driver.implicitly_wait(10)

    data = {
        "日付": datetime.now().strftime("%Y/%m/%d 15:30"),

        "現在値": driver.find_element(By.CSS_SELECTOR, ".basic-section__price__current").text.strip(),
        "前日比": driver.find_element(By.CSS_SELECTOR, ".basic-section__price__change").text.strip(),

        "始値": get(driver, "始値"),
        "高値": get(driver, "高値"),
        "安値": get(driver, "安値"),

        "年初来高値": get(driver, "年初来高値"),
        "年初来安値": get(driver, "年初来安値"),

        "出来高": get(driver, "出来高"),
        "売買代金": get(driver, "売買代金"),

        "22日平均": get(driver, "└ 22日平均"),
        "年初来株価上昇率": get(driver, "年初来株価上昇率"),
        "200日移動平均乖離率": get(driver, "200日移動平均乖離率"),
    }

    driver.quit()

    return data


def save(data):

    os.makedirs("output", exist_ok=True)

    path = "output/nikkei_avg_data.csv"
    exists = os.path.isfile(path)

    cols = list(data.keys())

    with open(path, "a", newline="", encoding="utf-8-sig") as f:
        w = csv.writer(f)

        if not exists:
            w.writerow(cols)

        w.writerow([data.get(c, "") for c in cols])


def main():

    try:
        data = fetch()
        save(data)
        print("saved")

    except Exception as e:
        print("error:", e)


if __name__ == "__main__":
    main()
