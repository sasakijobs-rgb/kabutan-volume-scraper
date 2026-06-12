import pandas as pd
import numpy as np
import re
from datetime import datetime
import os
from supabase import create_client


# =========================
# Supabase接続
# =========================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_ANON_KEY"]

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

TABLE_NAME = "trading_value_ranking"


# =========================
# 入力CSV
# =========================
inFile = "today"
# inFile = "trading_value_ranking_20260529.csv"

# =========================
# ファイル解決
# =========================
def resolve_input_file(inFile: str) -> str:

    if inFile == "today":
        today = datetime.now().strftime("%Y%m%d")
        file_path = f"output/trading_value_ranking_{today}.csv"
    else:
        file_path = f"output/{inFile}"

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"ファイルが存在しません: {file_path}")

    return file_path


# =========================
# 数値クレンジング（そのまま維持）
# =========================
def clean_financial_value(x):

    if pd.isna(x):
        return None

    x = str(x).strip()

    if "ー" in x or x in ["-", "―", "−"]:
        return None

    x = x.replace("倍", "")
    x = x.replace("％", "")
    x = x.replace("%", "")

    x = re.sub(r"[^0-9.\-]", "", x)

    if x == "":
        return None

    try:
        return float(x)
    except:
        return None


# =========================
# ETL（完全版）
# =========================
COLUMN_MAP = {
    "日付": "ymd",
    "順位": "rank",
    "銘柄名": "name",
    "コード": "code",
    "市場": "market",
    "状態": "status",
    "株価": "stock_price",
    "前日差": "diff_price",
    "騰落率": "diff_percent",
    "売買代金": "trade_value",
    "PER": "per",
    "PBR": "pbr",
    "配当利回り": "yld",
}


def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:

    # 日本語 → ローマ字
    df = df.rename(columns=COLUMN_MAP)

    # ---- カンマ除去 ----
    comma_cols = [
        "stock_price",
        "diff_price",
        "trade_value"
    ]
    for col in comma_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.replace(",", "", regex=False)
            .str.replace("+", "", regex=False)
        )

    # 数値系（安全変換）
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df["trade_value"] = pd.to_numeric(df["trade_value"], errors="coerce").astype("Int64")

    df["stock_price"] = pd.to_numeric(df["stock_price"], errors="coerce")
    df["diff_price"] = pd.to_numeric(df["diff_price"], errors="coerce")

    # 騰落率
    df["diff_percent"] = (
        df["diff_percent"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace("％", "", regex=False)
    )
    df["diff_percent"] = pd.to_numeric(df["diff_percent"], errors="coerce")

    # PER / PBR / YLD（元ロジック維持）
    df["per"] = df["per"].apply(clean_financial_value)
    df["pbr"] = df["pbr"].apply(clean_financial_value)
    df["yld"] = df["yld"].apply(clean_financial_value)

    # NaN → None（Supabase対策）
    df = df.where(pd.notnull(df), None)

    return df

# =========================
# NaN / NA / inf を完全排除
# =========================
def clean_for_supabase(df):
    df = df.copy()
    df = df.replace([np.nan, np.inf, -np.inf], None)
    return df

# =========================
# Supabase投入
# =========================
BATCH_SIZE = 500

def insert_to_supabase(df):

    data = df.to_dict(orient="records")
    total = len(data)

    print(f"[INFO] 開始: {total}件")

    for i in range(0, total, BATCH_SIZE):

        batch = data[i:i+BATCH_SIZE]

        supabase.table(TABLE_NAME).insert(batch).execute()

        print(
            f"[INFO] "
            f"{min(i+BATCH_SIZE, total)}/{total} 件完了"
        )

    print("[INFO] Supabase反映完了")

# =========================
# main
# =========================
if __name__ == "__main__":

    file_path = resolve_input_file(inFile)

    print("================================")
    print("読み込み:", file_path)
    print("================================")

    df = pd.read_csv(file_path)

    print("元件数:", len(df))
    print("元カラム:", df.columns.tolist())

    df = preprocess_df(df)

    print("================================")
    print("データのclean:", file_path)
    print("================================")
    df = clean_for_supabase(df)

    
    print("================================")
    print("変換後カラム:", df.columns.tolist())
    print(df.head(3))

    insert_to_supabase(df)

    print("DONE")
