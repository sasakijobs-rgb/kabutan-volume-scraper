import pandas as pd
import os
import time
import random
import requests
from bs4 import BeautifulSoup

# =========================
# 設定
# =========================
URL = "https://anarepo.kabucluster.com/?page=1"
OUTPUT_FILE = "output/EquityResearchReport.csv"


# =========================
# テキスト処理
# =========================
def clean_text(v):
    if v is None:
        return "-"
    return " ".join(str(v).replace("\n", " ").split())


def clean_number(v):
    if v is None:
        return None

    text = str(v).replace(",", "").replace("円", "").replace("%", "").strip()

    import re
    match = re.search(r"-?\d+(\.\d+)?", text)
    if not match:
        return None

    num = match.group()
    return float(num) if "." in num else int(num)


# =========================
# スクレイピング（page1固定）
# =========================
def scrape_page1():

    print(f"GET: {URL}")

    res = requests.get(URL, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    rows = soup.select("tr.hover")

    data = []

    for row in rows:

        th = row.select_one("th a")
        if not th:
            continue

        stock_text = clean_text(th.get_text(" ", strip=True)).split()

        if len(stock_text) < 2:
            continue

        code = stock_text[0]
        name = stock_text[-1]

        tds = row.find_all("td")
        if len(tds) < 8:
            continue

        data.append({
            "銘柄コード": code,
            "銘柄名": name,
            "現在株価": clean_number(tds[1].get_text()),
            "レポート公開日": clean_text(tds[2].get_text()),
            "発表機関": clean_text(tds[3].get_text()),
            "レポートタイトル": clean_text(tds[4].get_text(" ", strip=True)),
            "レーティング": clean_text(tds[5].get_text(" ", strip=True)),
            "目標株価": clean_number(tds[6].get_text()),
            "目標株価乖離率": clean_number(tds[7].get_text()),
        })

    return pd.DataFrame(data)


# =========================
# 保存
# =========================
def save_csv(df):

    os.makedirs("output", exist_ok=True)

    df.to_csv(
        OUTPUT_FILE,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"[SAVE] {OUTPUT_FILE} rows={len(df)}")


# =========================
# main
# =========================
if __name__ == "__main__":

    df = scrape_page1()

    print("raw rows:", len(df))
    print(df.head(3))

    save_csv(df)
