import pandas as pd
import numpy as np
import os
import time
import random
from datetime import datetime
from supabase import create_client

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "stock_reports"

TODAY = datetime.now().strftime("%Y-%m-%d")

# =========================
# クリーニング
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
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(",", "", regex=False)
                .str.replace("%", "", regex=False)
                .str.replace("円", "", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "report_date" in df.columns:
        df["report_date"] = pd.to_datetime(
            df["report_date"],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # ★ 今日だけ残す（重要）
    df = df[df["report_date"] == TODAY]

    df = df.replace([np.nan, np.inf, -np.inf], None)

    return df


# =========================
# upsert
# =========================
def insert(df):

    if df.empty:
        print("[SKIP] 今日データなし")
        return

    df = df.drop_duplicates(subset=["code", "report_date"], keep="last")
    
    records = df.to_dict("records")

    supabase.table(TABLE_NAME).upsert(
        records,
        on_conflict="code,report_date"
    ).execute()

    print(f"[OK] {len(records)} rows upserted")


# =========================
# scrape only page 1
# =========================
def scrape_page1():

    import requests
    from bs4 import BeautifulSoup

    url = "https://anarepo.kabucluster.com/?page=1"

    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("tr.hover")

    data = []

    for row in rows:

        th = row.select_one("th a")
        if not th:
            continue

        text = th.get_text(" ", strip=True).split()

        if len(text) < 2:
            continue

        code = text[0]
        name = text[-1]

        tds = row.find_all("td")
        if len(tds) < 8:
            continue

        data.append({
            "銘柄コード": code,
            "銘柄名": name,
            "現在株価": tds[1].text,
            "レポート公開日": tds[2].text,
            "発表機関": tds[3].text,
            "レポートタイトル": tds[4].text,
            "レーティング": tds[5].text,
            "目標株価": tds[6].text,
            "目標株価乖離率": tds[7].text,
        })

    return pd.DataFrame(data)


# =========================
# main
# =========================
if __name__ == "__main__":

    df = scrape_page1()

    print("raw:", len(df))

    df = preprocess(df)

    print("filtered:", len(df))

    insert(df)
