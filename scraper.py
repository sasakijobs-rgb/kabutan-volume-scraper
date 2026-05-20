from selenium import webdriver
from selenium.webdriver.common.by import By
import csv

date = "20260520"
page_no = 208
start_no = 4141

driver = webdriver.Chrome()
url = f"https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page={page_no}"
driver.get(url)

# tbodyのtrを全部取得
trs = driver.find_elements(By.CSS_SELECTOR, "div.gray-sticky-table table tbody tr")

raw_rows = []
for tr in trs:
    th = tr.find_element(By.TAG_NAME, "th")
    td_list = tr.find_elements(By.TAG_NAME, "td")
    
    # 銘柄名
    stock_name = th.find_element(By.TAG_NAME, "p").text
    # コードと市場
    code = th.find_element(By.CSS_SELECTOR, "div.flex.items-center").text.split()[0]
    market = th.find_element(By.CSS_SELECTOR, "div.flex.items-center span").text
    
    # 株価、前日比、売買代金、PER、PBR、利回り
    price = td_list[0].text
    diff_num = td_list[1].text.replace("\n", " ")
    sales = td_list[2].text
    per = td_list[4].text
    pbr = td_list[5].text
    yld = td_list[6].text
    
    # raw_data文字列作成
    raw = f"{stock_name} {code} {market} {price} {diff_num} {sales} {per} {pbr} {yld}"
    raw_rows.append(raw)

driver.quit()

# CSVに出力
with open("trading_value_ranking_20260520.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["日付", "順位", "raw_data"])
    for i, row in enumerate(raw_rows):
        writer.writerow([date, start_no + i, row])

print(f"[DONE] saved rows: {len(raw_rows)}")
