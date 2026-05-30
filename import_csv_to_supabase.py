import os
import pandas as pd
import numpy as np
from datetime import datetime
from supabase import create_client
import sys
import math

# ===============================
# Supabase設定
# ===============================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Supabase URLまたはKEYが設定されていません")
    sys.exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ===============================
# CSVパス
# ===============================
today_str = datetime.now().strftime("%Y%m%d")
file_path = f"output/trading_value_ranking_{today_str}.csv"

if not os.path.exists(file_path):
    print(f"CSVファイルが存在しません: {file_path}")
    sys.exit(0)

print(f"読み込むCSV: {file_path}")

# ===============================
# CSV読み込み
# ===============================
df = pd.read_csv(file_path)

# ===============================
# 日本語 → 英語カラム変換
# ===============================
df = df.rename(columns={
    "日付": "today",
    "順位": "rank_no",
    "銘柄名": "name",
    "コード": "code",
    "市場": "market",
    "状態": "status",
    "株価": "stock_price",
    "前日差": "diff_price",
    "騰落率": "diff_percent",
    "売買代金": "trade_value",
    "配当利回り": "yld"
})

# ===============================
# DBカラム以外を除外
# ===============================
db_columns = [
    "today",
    "rank_no",
    "name",
    "code",
    "market",
    "status",
    "stock_price",
    "diff_price",
    "diff_percent",
    "trade_value",
    "per",
    "pbr",
    "yld"
]

df = df[[c for c in df.columns if c in db_columns]]

# ===============================
# 数値変換関数
# ===============================
def to_number(x):
    if x is None:
        return None

    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None

    if isinstance(x, str):
        x = x.replace(",", "").strip()
        x = x.replace("ー倍", "")
        x = x.replace("ー%", "")
        x = x.replace("ー", "")
        if x == "":
            return None

    try:
        return float(x)
    except:
        return None

# ===============================
# 数値列変換
# ===============================
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
    if col in df.columns:
        df[col] = df[col].apply(to_number)

# ===============================
# rank_no型変換
# ===============================
if "rank_no" in df.columns:
    df["rank_no"] = pd.to_numeric(df["rank_no"], errors="coerce").astype("Int64")

# ===============================
# id列は送らない（DB管理）
# ===============================
df = df.drop(columns=["id"], errors="ignore")

# ===============================
# NaN / inf除去
# ===============================
df = df.replace([np.inf, -np.inf], np.nan)
df = df.astype(object).where(pd.notnull(df), None)

# ===============================
# records化
# ===============================
records = df.to_dict(orient="records")

# ===============================
# 最終チェック（デバッグ用）
# ===============================
for i, r in enumerate(records):
    for k, v in r.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            print(f"BAD VALUE -> row:{i}, col:{k}, value:{v}")
            sys.exit(1)

# ===============================
# Supabase insert
# ===============================
batch_size = 500
total_inserted = 0

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]

    response = supabase.table("trading_value_ranking").insert(batch).execute()

    if hasattr(response, "error") and response.error:
        print(f"エラー: {response.error}")
        sys.exit(1)

    total_inserted += len(batch)
    print(f"{total_inserted} 件登録完了")

print("CSVのSupabase取り込みが完了しました")
