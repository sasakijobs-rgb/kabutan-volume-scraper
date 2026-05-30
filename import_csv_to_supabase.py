import pandas as pd
import numpy as np
import re
from datetime import datetime
import os


# #####################################
# 入力ファイルパラメータ

inFile = "today"
# inFile = "trading_value_ranking_20260530.csv"

# #####################################


# =========================
# ファイル解決ロジック
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
# 数値クレンジング関数
# =========================
def clean_financial_value(x):
    """
    '23.7倍' → 23.7
    '5.2%' → 5.2
    'ー倍' / 'ー%' → None
    """
    if pd.isna(x):
        return None

    x = str(x).strip()

    # 欠損扱い
    if "ー" in x or x in ["-", "―", "−"]:
        return None

    # 単位削除
    x = x.replace("倍", "")
    x = x.replace("％", "")
    x = x.replace("%", "")

    # 数値以外除去
    x = re.sub(r"[^0-9.\-]", "", x)

    if x == "":
        return None

    try:
        return float(x)
    except:
        return None


# =========================
# ETL処理本体
# =========================
def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:

    # ---- 数値系 ----
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df["trade_value"] = pd.to_numeric(df["trade_value"], errors="coerce").astype("Int64")

    df["stock_price"] = pd.to_numeric(df["stock_price"], errors="coerce")
    df["diff_price"] = pd.to_numeric(df["diff_price"], errors="coerce")

    # ---- 騰落率 ----
    df["diff_percent"] = (
        df["diff_percent"]
        .astype(str)
        .str.replace("%", "", regex=False)
        .str.replace("％", "", regex=False)
    )
    df["diff_percent"] = pd.to_numeric(df["diff_percent"], errors="coerce")

    # ---- PER / PBR / YLD ----
    df["per"] = df["per"].apply(clean_financial_value)
    df["pbr"] = df["pbr"].apply(clean_financial_value)
    df["yld"] = df["yld"].apply(clean_financial_value)

    # ---- NULL統一 ----
    numeric_cols = [
        "stock_price",
        "diff_price",
        "diff_percent",
        "trade_value",
        "per",
        "pbr",
        "yld"
    ]

    for col in numeric_cols:
        df[col] = df[col].replace({np.nan: None})

    return df


# =========================
# メイン処理
# =========================
if __name__ == "__main__":

    # ファイル決定
    file_path = resolve_input_file(inFile)

    print("================================")
    print("読み込みファイル:", file_path)
    print("================================")

    # CSV読み込み
    df = pd.read_csv(file_path)

    print("元データ件数:", len(df))

    # 変換処理
    df = preprocess_df(df)

    print("================================")
    print("✔ 変換完了（Supabase投入準備OK）")
    print(df.head(3))
