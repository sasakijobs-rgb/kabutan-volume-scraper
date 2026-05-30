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
# CSVファイル
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
# 列名をアルファベット化（DBに合わせる）
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
    "PER": "per",
    "PBR": "pbr",
    "配当利回り": "yld"
})

# ===============================
# 数値変換関数（完全対応）
# ===============================
def to_number(x):
    if x is None:
        return None

    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None

    if isinstance(x, str):
        x = x.replace(",", "").replace("%", "").replace("ー倍", "").replace("ー%", "").strip()
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
# 型変換
# ===============================
if "rank_no" in df.columns:
    df["rank_no"] = pd.to_numeric(df["rank_no"], errors="coerce").astype("Int64")

if "code" in df.columns:
    df["code"] = df["code"].astype(str)

if "today" in df.columns:
    df["today"] = pd.to_datetime(df["today"], format="%Y%m%d").dt.date

# ===============================
# 当日データのみ抽出
# ===============================
today_date = datetime.now().date()
df = df[df["today"] == today_date]

# ===============================
# NaN / inf 完全除去（超重要）
# ===============================
df = df.replace([np.inf, -np.inf], np.nan)
df = df.astype(object).where(pd.notnull(df), None)

# ===============================
# records化（安全化）
# ===============================
def clean(x):
    if x is None:
        return None
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None
    return x

records = [
    {k: clean(v) for k, v in row.items()}
    for row in df.to_dict(orient="records")
]

# ===============================
# デバッグ（異常値検知）
# ===============================
for i, r in enumerate(records):
    for k, v in r.items():
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            print(f"BAD VALUE -> row:{i}, col:{k}, value:{v}")
            sys.exit(1)

# ===============================
# Supabase upsert（重複防止、today+rank_no）
# ===============================
batch_size = 500
total_inserted = 0

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]

    response = (
        supabase
        .table("trading_value_ranking")
        .upsert(batch, on_conflict="today,rank_no")
        .execute()
    )

    if hasattr(response, "error") and response.error:
        print(f"エラー: {response.error}")
        sys.exit(1)

    total_inserted += len(batch)
    print(f"{total_inserted} 件登録完了")

print("CSVのSupabase取り込みが完了しました")
