import os
import re
import time
import random
import pandas as pd

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

from supabase import create_client

# =====================================
# Supabase接続
# =====================================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "stock_reports"

# =====================================
# パラメータ
# =====================================
prm = "one"
# one / select

START_PAGE = 501
END_PAGE = 600

# =====================================
# テキスト整形
# =====================================
def clean_text(value):

    if value is None:
        return None

    text = str(value)

    text = text.replace("\r", " ")
    text = text.replace("\n", " ")

    text = " ".join(text.split())

    if text == "":
        return None

    if text == "-":
        return None

    return text


# =====================================
# 数値整形
# =====================================
def clean_number(value):

    if value is None:
        return None

    text = str(value).strip()

    if text in ["", "-"]:
        return None

    text = (
        text.replace(",", "")
            .replace("円", "")
            .replace("%", "")
            .replace("+", "")
            .replace("　", "")
            .strip()
    )

    match = re.search(r"-?\d+(\.\d+)?", text)

    if not match:
        return None

    num = match.group()

    return float(num) if "." in num else int(num)


# =====================================
# ページ設定
# =====================================
if prm == "one":
    pages = [1]

elif prm == "select":
    pages = range(START_PAGE, END_PAGE + 1)

else:
    raise ValueError("prm は one または select を指定してください")


# =====================================
# Selenium起動
# =====================================
options = Options()
options.add_argument("--headless=new")
options.add_argument("--disable-gpu")

driver = webdriver.Chrome(options=options)


# =====================================
# 取得開始
# =====================================
data = []
seen = set()

for page in pages:

    url = f"https://anarepo.kabucluster.com/?page={page}"

    print(f"取得中 : {url}")

    try:
        driver.get(url)

        time.sleep(random.choice([0.5, 1.0, 1.5]))

        soup = BeautifulSoup(driver.page_source, "html.parser")

        rows = soup.select("tr.hover")

        print(f"page={page} rows={len(rows)}")

        for row in rows:

            th = row.select_one("th a")
            if not th:
                continue

            stock_text = clean_text(th.get_text(" ", strip=True))
            if not stock_text:
                continue

            parts = stock_text.split()
            if len(parts) < 2:
                continue

            stock_code = parts[0]
            stock_name = parts[-1]

            tds = row.find_all("td")
            if len(tds) < 8:
                continue

            current_price = clean_number(tds[1].get_text())
            report_date = clean_text(tds[2].get_text())
            company = clean_text(tds[3].get_text())
            title = clean_text(tds[4].get_text(" ", strip=True))
            rating = clean_text(tds[5].get_text(" ", strip=True))
            target_price = clean_number(tds[6].get_text())

            deviation_tag = tds[7].select_one("svg text")
            deviation = clean_number(deviation_tag.get_text() if deviation_tag else None)

            key = (stock_code, report_date)
            if key in seen:
                continue
            seen.add(key)

            data.append({
                "銘柄コード": stock_code,
                "銘柄名": stock_name,
                "現在株価": current_price,
                "レポート公開日": report_date,
                "発表機関": company,
                "レポートタイトル": title,
                "レーティング": rating,
                "目標株価": target_price,
                "目標株価乖離率": deviation,
                "取得ページ": page
            })

    except Exception as e:
        print(f"page={page} エラー")
        print(e)
        continue

driver.quit()


# =====================================
# DataFrame化
# =====================================
df = pd.DataFrame(data)

print(f"取得件数: {len(df)}")


# =====================================
# CSV保存
# =====================================
os.makedirs("output", exist_ok=True)

if prm == "one":
    filename = "output/EquityResearchReport_page1.csv"

else:
    filename = f"output/EquityResearchReport_{START_PAGE}_{END_PAGE}.csv"

df.to_csv(filename, index=False, encoding="utf-8-sig")

print("保存完了:", filename)


# =====================================
# Supabase用前処理
# =====================================
df = df.replace("-", None)

df = df.rename(columns={
    "銘柄コード": "code",
    "銘柄名": "name",
    "現在株価": "stock_price",
    "レポート公開日": "report_date",
    "発表機関": "broker",
    "レポートタイトル": "title",
    "レーティング": "rating",
    "目標株価": "target_price",
    "目標株価乖離率": "target_gap",
    "取得ページ": "source_page",
})

df = df.replace(["-", "―", "ー"], None)

df = df.where(pd.notnull(df), None)


# 日付（Supabase用：文字列）
if "report_date" in df.columns:
    df["report_date"] = (
        df["report_date"]
        .astype(str)
        .str.extract(r"(\d{4}/\d{2}/\d{2})")[0]
    )

    df["report_date"] = pd.to_datetime(
        df["report_date"],
        errors="coerce"
    ).dt.strftime("%Y-%m-%d")


# 数値変換
num_cols = ["stock_price", "target_price", "target_gap"]

for col in num_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")


# BOM対策（重要）
df.columns = df.columns.str.replace("\ufeff", "").str.strip()


# =====================================
# Supabase insert
# =====================================
BATCH_SIZE = 500

records = df.to_dict(orient="records")

print(f"[INFO] Supabase insert開始: {len(records)}件")

for i in range(0, len(records), BATCH_SIZE):

    batch = records[i:i+BATCH_SIZE]

    supabase.table(TABLE_NAME).insert(batch).execute()

    print(f"[OK] {min(i+BATCH_SIZE, len(records))}/{len(records)}")

print("[DONE] Supabase反映完了")
