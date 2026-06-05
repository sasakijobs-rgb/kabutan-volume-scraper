import pandas as pd
import numpy as np
import re
import os
from datetime import datetime
from supabase import create_client

# =========================
# Supabase接続
# =========================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "stock_reports"

# =========================
# 入力CSV
# =========================
IN_FILE = "EquityResearchReport.csv"


# =========================
# ファイルチェック
# =========================
def resolve_file():
    file_path = f"output/{IN_FILE}"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"CSVが見つかりません: {file_path}")

    return file_path


# =========================
# クレンジング
# =========================
def preprocess(df: pd.DataFrame) -> pd.DataFrame:

    # -------------------------
    # 欠損・ハイフン統一
    # -------------------------
    df = df.replace("-", None)

    # -------------------------
    # カラム名整理
    # -------------------------
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

    # -------------------------
    # 数値変換
    # -------------------------
    num_cols = ["stock_price", "target_price", "target_gap"]

    for col in num_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("%", "", regex=False)
            .str.replace("円", "", regex=False)
        )
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # -------------------------
    # 日付処理
    # -------------------------
    df["report_date"] = (
        df["report_date"]
        .astype(str)
        .str.extract(r"(\d{4}/\d{2}/\d{2})")[0]
    )

    df["report_date"] = pd.to_datetime(df["report_date"], errors="coerce").dt.date

    # -------------------------
    # 不要列削除
    # -------------------------
    if "source_page" in df.columns:
        df = df.drop(columns=["source_page"])

    # -------------------------
    # Supabase対策
    # -------------------------
    df = df.replace([np.nan, np.inf, -np.inf], None)

    return df


# =========================
# Supabase insert
# =========================
BATCH_SIZE = 500

def insert(df):

    records = df.to_dict(orient="records")

    print(f"[INFO] insert開始: {len(records)}件")

    for i in range(0, len(records), BATCH_SIZE):
        batch = records[i:i+BATCH_SIZE]

        supabase.table(TABLE_NAME).insert(batch).execute()

        print(f"[OK] {min(i+BATCH_SIZE, len(records))}/{len(records)}")

    print("[DONE] 完了")


# =========================
# main
# =========================
if __name__ == "__main__":

    file_path = resolve_file()

    print("================================")
    print("INPUT:", file_path)
    print("================================")

    df = pd.read_csv(file_path)

    print("rows:", len(df))

    df = preprocess(df)

    print("================================")
    print("preview")
    print(df.head(3))

    insert(df)
