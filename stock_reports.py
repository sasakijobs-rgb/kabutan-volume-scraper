import pandas as pd
import numpy as np
from supabase import create_client
import os

# =========================
# Supabase接続
# =========================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "stock_reports"

# =========================
# 前処理
# =========================
def preprocess(df: pd.DataFrame) -> pd.DataFrame:
    # BOM除去
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()
    
    # ハイフンや空文字をNaN
    df = df.replace(["-", "―", "−", "ー", ""], np.nan)
    
    # カラム名統一
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
    
    # 数値変換
    for col in ["stock_price", "target_price", "target_gap"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col].astype(str)
                                    .str.replace(",", "", regex=False)
                                    .str.replace("%", "", regex=False)
                                    .str.replace("円", "", regex=False), errors="coerce")
    
    # 日付変換
    if "report_date" in df.columns:
        df["report_date"] = pd.to_datetime(
            df["report_date"].astype(str).str.extract(r"(\d{4}/\d{2}/\d{2})")[0],
            errors="coerce"
        ).dt.strftime("%Y-%m-%d")
    
    # Supabase安全化
    df = df.replace([np.nan, np.inf, -np.inf], None)
    
    return df

# =========================
# Supabaseへ送信
# =========================
def insert(df: pd.DataFrame):
    records = df.to_dict(orient="records")
    supabase.table(TABLE_NAME).upsert(records, on_conflict="code,report_date").execute()
    print(f"[INFO] {len(records)} rows upserted")

# =========================
# main
# =========================
if __name__ == "__main__":
    # ここでスクレイピングした1ページ目を df に格納
    df = scrape_page1()  # ← 既存のスクレイピング関数

    # 今日の日付だけ残す
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    df = df[df["report_date"] == today].reset_index(drop=True)
    
    if df.empty:
        print("[INFO] 本日のデータなし")
    else:
        df = preprocess(df)
        df = df.drop_duplicates(subset=["code", "report_date"]).reset_index(drop=True)
        insert(df)
