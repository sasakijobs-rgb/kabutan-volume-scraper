import requests
from bs4 import BeautifulSoup

url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

headers = {
    "User-Agent": "Mozilla/5.0"
}

res = requests.get(url, headers=headers)
res.raise_for_status()

soup = BeautifulSoup(res.text, "html.parser")

# テーブル取得
table = soup.find("table")

rows = table.find_all("tr")[1:16]  # ヘッダー除いて15件

data = []

for row in rows:
    cols = row.find_all("td")
    
    if len(cols) < 4:
        continue

    code = cols[0].text.strip()
    name = cols[1].text.strip()
    price = cols[2].text.strip()
    value = cols[3].text.strip()

    data.append([code, name, price, value])

# 表示
for d in data:
    print(d)
