import re
import csv
import time
from selenium import webdriver
from selenium.webdriver.common.by import By

DATE = "20260520"
BASE_URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page="
OUTPUT_FILE = f"trading_value_ranking_{DATE}.csv"


# =========================
# 件数 → 最終ページ
# =========================
def calc_last_page(total):
    return (total + 19) // 20


# =========================
# 件数取得
# =========================
def get_total(driver):
    driver.get(BASE_URL + "1")
    time.sleep(2)

    text = driver.page_source
    m = re.search(r"([\d,]+)件\s*/\s*([\d,]+)件中", text)

    if not m:
        raise Exception("件数が取得できません")

    return int(m.group(2).replace(",", ""))


# =========================
# 通常ページ
# =========================
def parse_normal(driver, page):
    url = BASE_URL + str(page)
    driver.get(url)
    time.sleep(2)

    rows = []

    trs = driver.find_elements(By.CSS_SELECTOR, "tbody tr")

    no = (page - 1) * 20 + 1

    for tr in trs:
        tds = tr.find_elements(By.TAG_NAME, "td")
        if len(tds) < 8:
            continue

        try:
            head = tr.find_element(By.TAG_NAME, "th").text
            parts = head.split()

            name = parts[0]
            code = parts[1]
            market = parts[2]

            price = tds[0].text
            change = tds[1].text.split("\n")[0]
            change_pct = tds[1].text.split("\n")[1]
            volume = tds[2].text
            per = tds[3].text
            pbr = tds[4].text
            yield_ = tds[5].text

            rows.append([
                DATE, no, code, name, market,
                price, change, change_pct,
                volume, per, pbr, yield_
            ])
            no += 1

        except:
            continue

    return rows


# =========================
# 最終ページ（崩れ対応）
# =========================
def parse_last(driver, page):
    url = BASE_URL + str(page)
    driver.get(url)
    time.sleep(2)

    html = driver.page_source
    text = re.sub(r"<br\s*/?>", "\n", html)
    text = re.sub(r"<.*?>", "", text)

    lines = text.split("\n")

    rows = []
    no = (page - 1) * 20 + 1

    for line in lines:
        line = line.strip()

        # 銘柄行っぽいものだけ拾う
        if not re.search(r"\d{4}\s東|名|札|福", line):
            continue

        parts = line.split()

        if len(parts) < 9:
            continue

        try:
            name = parts[0]
            code = parts[1]
            market = parts[2]
            price = parts[3]
            change = parts[4]
            change_pct = parts[5]
            volume = parts[6]
            per = parts[7]
            pbr = parts[8]
            yield_ = parts[9] if len(parts) > 9 else "-"

            rows.append([
                DATE, no, code, name, market,
                price, change, change_pct,
                volume, per, pbr, yield_
            ])
            no += 1

        except:
            continue

    return rows


# =========================
# CSV出力
# =========================
def save(rows):
    header = [
        "日付","No","コード","銘柄名","市場",
        "株価(百万円)","前日比","前日比(%)",
        "売買代金","PER","PBR","利回り"
    ]

    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)


# =========================
# MAIN
# =========================
def main():
    print("===== START =====")

    driver = webdriver.Chrome()

    total = get_total(driver)
    last_page = calc_last_page(total)

    print(f"[INFO] total: {total}")
    print(f"[INFO] last_page: {last_page}")

    all_rows = []

    # 1ページ目
    print("[PAGE 1]")
    all_rows += parse_normal(driver, 1)

    # 最終ページ
    print(f"[PAGE {last_page}]")
    all_rows += parse_last(driver, last_page)

    save(all_rows)

    driver.quit()

    print("===== DONE =====")
    print(f"file: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
