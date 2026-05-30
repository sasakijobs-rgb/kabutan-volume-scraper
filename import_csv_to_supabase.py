import pandas as pd
import numpy as np
import re


# =========================
# ① 数値クレンジング関数
# =========================
def clean_financial_value(x):
    """
    ・'23.7倍' → 23.7
    ・'5.2%' / '5.2％' → 5.2
    ・'ー倍' / 'ー%' → None
    """
    if pd.isna(x):
        return None

    x = str(x).strip()

    # 欠損表現
    if "ー" in x or x in ["-", "―", "−"]:
        return None

    # 単位除去
    x = x.replace("倍", "")
    x = x.replace("％", "")
    x = x.replace("%", "")

    # 数値以外を除去
    x = re.sub(r"[^0-9.\-]", "", x)

    if x == "":
        return None

    try:
        return float(x)
    except:
        return None


# =========================
# ② メイン変換処理（軽量版）
# =========================
def preprocess_df(df: pd.DataFrame) -> pd.DataFrame:

    # ---- 数値（整数系）----
    df["rank"] = pd.to_numeric(df["rank"], errors="coerce").astype("Int64")
    df["trade_value"] = pd.to_numeric(df["trade_value"], errors="coerce").astype("Int64")

    # ---- 株価系 ----
    df["stock_price"] = pd.to_numeric(df["stock_price"], errors="coerce")
    df["diff_price"] = pd.to_numeric(df["diff_price"], errors="coerce")

    # ---- 騰落率（%除去）----
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

    # =========================
    # ③ 最終NULL統一
    # =========================
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
# ③ 使用例
# =========================
if __name__ == "__main__":

    df = pd.read_csv("output/trading_value_ranking_20260530.csv")

    print("変換前件数:", len(df))

    df = preprocess_df(df)

    print("変換後サンプル:")
    print(df.head(3))

    print("✔ Supabase投入準備完了（日時処理なし）")
