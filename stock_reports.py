import os
import re
import time
import random
import pandas as pd

from supabase import create_client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# =========================================================
# 🔧 パラメータ設定 one:1ページ目だけ select:ページ指定
# =========================================================

MODE = "one"  
# MODE = "select"

START_PAGE = 501
END_PAGE = 600

BASE_URL = "https://anarepo.kabucluster.com/?page={page}"

SLEEP_RANGE = (0.5, 1.2)

TABLE_NAME = "stock_reports"

BATCH_SIZE = 500

UNIQUE_KEYS = ["code", "report_date"]

SAVE_CSV = False  # TrueにするとCSV保存

# =========================================================
# Supabase
# =========================================================
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# =========================================================
# ページ生成
# =========================================================
if MODE == "one":
    pages = [1]
elif MODE == "select":
    pages = range(START_PAGE, END_PAGE + 1)
else:
    raise ValueError("MODE must be 'one' or 'select'")

# =========================================================
# helper
# =========================================================
def clean_text(v):
    if v is None:
        return "-"
    v = str(v).replace("\n", " ").replace("\r", " ")
    return " ".join(v.split()) or "-"

def clean_number(v):
    if v is None:
        return "-"
    v = str(v)
    v = re.sub(r"[^\d\.\-]", "", v)
    if v == "":
        return "-"
    return float(v) if "." in v else int(v)

# =========================================================
# Selenium
# =========================================================
options = Options()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

data = []
seen = set()

# =========================================================
# scrape
# =========================================================
for page in pages:

    url = BASE_URL.format(page=page)
    print("GET:", url)

    driver.get(url)
    time.sleep(random.uniform(*SLEEP_RANGE))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("tr.hover")

    for row in rows:

        th = row.select_one("th a")
        if not th:
            continue

        text = clean_text(th.get_text(" ", strip=True))
        parts = text.split()

        if len(parts) < 2:
            continue

        code = parts[0]
        name = parts[-1]

        tds = row.find_all("td")
        if len(tds) < 8:
            continue

        report_date = clean_text(tds[2].get_text())

        key = (code, report_date)
        if key in seen:
            continue
        seen.add(key)

        data.append({
            "code": code,
            "name": name,
            "stock_price": clean_number(tds[1].get_text()),
            "report_date": report_date,
            "broker": clean_text(tds[3].get_text()),
            "title": clean_text(tds[4].get_text(" ", strip=True)),
            "rating": clean_text(tds[5].get_text(" ", strip=True)),
            "target_price": clean_number(tds[6].get_text()),
            "target_gap": clean_number(tds[7].get_text()),
            "page": page
        })

driver.quit()

df = pd.DataFrame(data)
print("rows:", len(df))

# =========================================================
# Supabase upsert
# =========================================================
def insert(df):

    df = df.replace("-", None)
    records = df.to_dict(orient="records")

    print(f"[UPSERT] {len(records)} rows")

    for i in range(0, len(records), BATCH_SIZE):

        batch = records[i:i+BATCH_SIZE]

        supabase.table(TABLE_NAME).upsert(
            batch,
            on_conflict="code,report_date"
        ).execute()

        print(f"{min(i+BATCH_SIZE, len(records))}/{len(records)}")

insert(df)

print("DONE")
