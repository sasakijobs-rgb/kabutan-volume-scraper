options.add_argument("--disable-gpu")
options.add_argument("--window-size=1920,1080")

# bot判定軽減
options.add_argument(
    "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    "--user-agent=Mozilla/5.0"
)

# =========================
@@ -52,7 +51,6 @@

driver.get(url)

# JS描画待ち
time.sleep(5)

print("ページタイトル:", driver.title)
@@ -72,35 +70,40 @@
for row in rows:

try:

# =========================
        # th取得
        # 銘柄名取得
# =========================
        ths = row.find_elements(By.TAG_NAME, "th")
        name_elem = row.find_elements(
            By.CSS_SELECTOR,
            "th a p, th a abbr"
        )

        # thが無い行はスキップ
        if not ths:
        if not name_elem:
continue

        th = ths[0]
        name = name_elem[0].text.strip()

        parts = th.text.split()

        # 初期化
        name = ""
        # =========================
        # コード・市場取得
        # =========================
code = ""
market = ""

        # =========================
        # データ解析
        # =========================
        if len(parts) >= 1:
            name = parts[0]
        code_market = row.find_elements(
            By.CSS_SELECTOR,
            "th a div.flex"
        )

        if len(parts) >= 2:
            code = parts[1]
        if code_market:

        if len(parts) >= 3:
            market = parts[2]
            parts = code_market[0].text.split()

            if len(parts) >= 1:
                code = parts[0].strip()

            if len(parts) >= 2:
                market = parts[1].strip()

# =========================
# td取得
@@ -111,14 +114,18 @@
continue

price = tds[0].text.strip()
        diff = tds[1].text.strip()
        diff_percent = tds[2].text.strip()

        # 前日比
        diff_parts = tds[1].text.split("\n")

        diff = diff_parts[0].strip() if len(diff_parts) > 0 else ""
        diff_percent = diff_parts[1].strip() if len(diff_parts) > 1 else ""

trading_value = tds[3].text.strip()
per = tds[4].text.strip()
pbr = tds[5].text.strip()
dividend = tds[6].text.strip()

        # デバッグ表示
print(
code,
name,
@@ -132,7 +139,9 @@
dividend
)

        # データ保存
        # =========================
        # 保存
        # =========================
data.append([
code,
name,
@@ -146,7 +155,6 @@
dividend
])

        # 15件だけ
if len(data) >= 15:
break

@@ -161,7 +169,7 @@
# =========================
# CSV保存
# =========================
with open(file_path, "w", newline="", encoding="utf-8") as f:
with open(file_path, "w", newline="", encoding="utf-8-sig") as f:

writer = csv.writer(f)
