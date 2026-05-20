import requests
from bs4 import BeautifulSoup

# =========================
# URL
# =========================
url = "https://kabutan.jp/warning/trading_value_ranking?market=0&capitalization=-1&dispmode=normal&stc=&stm=0&page=1"

print("===== START =====")
print("URL:", url)

# =========================
# ヘッダー（最低限のブラウザ偽装）
# =========================
headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
}

# =========================
# リクエスト
# =========================
print("===== REQUEST =====")

res = requests.get(url, headers=headers, timeout=15)

print("STATUS:", res.status_code)
print("FINAL URL:", res.url)
print("HTML SIZE:", len(res.text))

html = res.text

# =========================
# WAFチェック
# =========================
if "Human Verification" in html or "captcha" in html.lower():
    print("\n❌ WAF検知されました（HTML取得できていません）")
    print(html[:1000])
    exit()

# =========================
# パース
# =========================
soup = BeautifulSoup(html, "html.parser")

table = soup.select_one("table.stock_table.st_market")

print("\n===== TABLE CHECK =====")
print("table exists:", table is not None)

if not table:
    print("❌ テーブルが取得できません（構造 or WAF）")
    exit()

rows = table.select("tbody tr")

print("row count:", len(rows))

if len(rows) == 0:
    print("❌ 行が取得できません")
    exit()

# =========================
# 1件取得テスト
# =========================
row = rows[0]

print("\n===== RAW ROW TEXT =====")
print(row.get_text(" ", strip=True))

tds = row.find_all("td")
ths = row.find_all("th")

print("\n===== DEBUG =====")
print("td count:", len(tds))
print("th count:", len(ths))

# =========================
# 項目抽出（構造確認用）
# =========================
try:
    code = tds[0].text.strip()
    name = ths[0].text.strip()
    market = tds[1].text.strip()

    price = tds[4].text.strip()
    change = tds[6].text.strip()
    change_pct = tds[7].text.strip()
    value = tds[8].text.strip()
    per = tds[9].text.strip()
    pbr = tds[10].text.strip()
    yield_ = tds[11].text.strip()

    print("\n===== RESULT (1件) =====")
    print("コード:", code)
    print("銘柄名:", name)
    print("市場:", market)
    print("株価:", price)
    print("前日比:", change)
    print("前日比%:", change_pct)
    print("売買代金:", value)
    print("PER:", per)
    print("PBR:", pbr)
    print("利回り:", yield_)

except Exception as e:
    print("\n❌ パースエラー")
    print(e)

print("\n===== END =====")
