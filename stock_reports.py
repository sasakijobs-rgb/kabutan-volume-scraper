import os
import re
import time
import random
import pandas as pd
import numpy as np

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from supabase import create_client

# =========================
# Supabase
# =========================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "stock_reports"

# =========================
# スクレイピング
# =========================
def scrape_page1():

    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")

    driver = webdriver.Chrome(options=options)

    url = "https://anarepo.kabucluster.com/?page=1"
    driver.get(url)

    time.sleep(random.choice([0.5, 1.0, 1.5]))

    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("tr.hover")

    data = []
    seen = set()

    for row in rows:

        th = row.select_one("th a")
        if not th:
            continue

        stock_text = th.get_text(" ", strip=True).split()
        if len(stock_text) < 2:
            continue

        code = stock_text[0]
        name = stock_text[-1]

        tds = row.find_all("td")
        if len(tds) < 8:
            continue

        report_date = tds[2].get_text(strip=True)

        key = (code, report_date)
        if key in seen:
            continue
        seen.add(key)

        data.append({
            "銘柄コード": code,
            "銘柄名": name,
            "現在株価": tds[1].get_text(strip=True),
            "レポート公開日": report_date,
            "発表機関": tds[3].get_text(strip=True),
            "レポートタイトル": tds[4].get_text(strip=True),
            "レーティング": tds[5].get_text(strip=True),
            "目標株価": tds[6].get_text(strip=True),
            "目標株価乖離率": tds[7].get_text(strip=True),
        })

    driver.quit()

    return pd.DataFrame(data)

# =========================
# 前処理
# =========================
def preprocess(df):

    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()
    df = df.replace(["-", "―", "−", "ー", ""], np.nan)

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
    })

    for col in ["stock_price", "target_price", "target_gap"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    df["report_date"] = pd.to_datetime(
        df["report_date"], errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    df = df.replace([np.nan, np.inf, -np.inf], None)

    return df

# =========================
# Supabase
# =========================
def insert(df):

    if df.empty:
        print("[INFO] データなし")
        return

    records = df.to_dict(orient="records")

    supabase.table(TABLE_NAME).upsert(
        records,
        on_conflict="code,report_date"
    ).execute()

    print(f"[OK] {len(records)} rows upserted")

# =========================
# main
# =========================
if __name__ == "__main__":

    # ① まずスクレイピング
    df = scrape_page1()

    print("raw:", len(df))

    # ② 前処理
    df = preprocess(df)

    print("filtered:", len(df))

    # ③ Supabase送信
    insert(df)

    print("DONE")
