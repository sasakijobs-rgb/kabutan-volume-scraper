import pandas as pd
import numpy as np
import os
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
# ファイル
# =========================
def resolve_file():
    path = f"output/{IN_FILE}"
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    return path


# =========================
# 前処理
# =========================
def preprocess(df: pd.DataFrame) -> pd.DataFrame:

    # ★ BOM完全除去（重要）
    df.columns = df.columns.str.replace("\ufeff", "", regex=False).str.strip()

    # -------------------------
    # ハイフン統一
    # -------------------------
    df = df.replace(["-", "―", "−", "ー", ""], np.nan)

    # -------------------------
    # rename
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
    # 数値
    # -------------------------
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

    # -------------------------
    # 日付（安全）
    # -------------------------
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

    # -------------------------
    # 不要列
    # -------------------------
    if "source_page" in df.columns:
        df = df.drop(columns=["source_page"])

    # -------------------------
    # Supabase安全化（超重要）
    # -------------------------
    df = df.replace([np.nan, np.inf, -np.inf], None)

    return df


# =========================
# insert
# =========================
def insert(df):

    batch_size = 500
    records = df.to_dict(orient="records")

    print(f"[INFO] insert: {len(records)} rows")

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]

        supabase.table(TABLE_NAME).upsert(
            batch,
            on_conflict="code,report_date"
        ).execute()

        print(f"[OK] {min(i+batch_size, len(records))}/{len(records)}")


# =========================
# main
# =========================
if __name__ == "__main__":

    file_path = resolve_file()

    print("================================")
    print("INPUT:", file_path)
    print("================================")

    df = pd.read_csv(
        file_path,
        skiprows=lambda x: x == 0 or "===" in str(x),
        encoding="utf-8-sig"
    )

    print("rows:", len(df))

    df = preprocess(df)

    print("================================")
    print("preview")
    print(df.head(3))

    print("report_date sample:")
    print(df["report_date"].dropna().head(5))

    insert(df)
