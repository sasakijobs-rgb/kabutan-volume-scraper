import os
import re
import time
import random
import yaml
import pandas as pd

from supabase import create_client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

# =========================
# YAML読み込み
# =========================
with open("stock_reports.yaml", "r", encoding="utf-8") as f:
    cfg = yaml.safe_load(f)

MODE = cfg["mode"]
TABLE_NAME = cfg["supabase"]["table"]
UNIQUE_KEYS = cfg["supabase"]["unique_keys"]

# =========================
# Supabase接続
# =========================
supabase = create_client(
    os.environ["SUPABASE_URL"],
    os.environ["SUPABASE_KEY"]
)

# =========================
# ページ設定
# =========================
if MODE == "one":
    pages = [1]
elif MODE == "select":
    pages = range(cfg["pages"]["start"], cfg["pages"]["end"] + 1)
else:
    raise ValueError("mode must be one or select")

# =========================
# クレンジング
# =========================
def clean_text(v):
    if v is None:
        return "-"
    v = str(v).replace("\n", " ").replace("\r", " ")
    v = " ".join(v.split())
    return v or "-"


def clean_number(v):
    if v is None:
        return "-"
    v = str(v)
    v = re.sub(r"[^\d\.\-]", "", v)
    if v == "":
        return "-"
    return float(v) if "." in v else int(v)

# =========================
# Selenium
# =========================
options = Options()
options.add_argument("--headless=new")

driver = webdriver.Chrome(options=options)

data = []
seen = set()

# =========================
# scrape
# =========================
for page in pages:

    url = f"https://anarepo.kabucluster.com/?page={page}"
    print("GET:", url)

    driver.get(url)
    time.sleep(random.uniform(0.5, 1.2))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("tr.hover")

    print(f"page={page} rows={len(rows)}")

    for row in rows:

        th = row.select_one("th a")
        if not th:
            continue

        stock_text = clean_text(th.get_text(" ", strip=True))
        parts = stock_text.split()

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

# =========================
# Supabase insert（upsert）
# =========================
def insert(df):

    df = df.replace("-", None)

    records = df.to_dict(orient="records")

    print(f"[UPSERT] {len(records)} rows")

    for i in range(0, len(records), 500):

        batch = records[i:i+500]

        supabase.table(TABLE_NAME).upsert(
            batch,
            on_conflict="code,report_date"
        ).execute()

        print(f"{min(i+500, len(records))}/{len(records)}")

insert(df)

print("DONE")
