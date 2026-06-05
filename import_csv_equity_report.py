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
