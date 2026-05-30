import os
import pandas as pd
import numpy as np
from datetime import datetime, date
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
# カラム名変換
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
# 数値変換
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

# ===============================
# 日付変換（安全版）
# ===============================
def parse_date(col):
    col = col.astype(str).str.strip()
    col = col.str.replace("-", "")
    col = col.str.replace("/", "")
    col = col.str.replace(".0", "", regex=False)

    return pd.to_datetime(col, format="%Y%m%d", errors="coerce").dt.date


if "today" in df.columns:
    df["today"] = parse_date(df["today"])

# ===============================
# デバッグ
# ===============================
print("=== 日付デバッグ ===")
print("NaT件数:", df["today"].isna().sum())
print("例:", df["today"].dropna().head(5).tolist())

# ===============================
# フィルタ（必要なら残す）
# ===============================
today_date = datetime.now().date()

df_before_filter = len(df)
df = df[df["today"] == today_date]
df_after_filter = len(df)

# ===============================
# NaN / inf処理
# ===============================
df = df.replace([np.inf, -np.inf], np.nan)
df = df.astype(object).where(pd.notnull(df), None)

# ===============================
# JSON安全化（重要修正ポイント）
# ===============================
def clean(x):
    if x is None:
        return None

    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return None

    # pandas timestamp
    if isinstance(x, pd.Timestamp):
        return x.isoformat()

    # datetime.date / datetime.datetime
    if isinstance(x, (datetime, date)):
        return x.isoformat()

    return x


records = [
    {k: clean(v) for k, v in row.items()}
    for row in df.to_dict(orient="records")
]

# ===============================
# Supabase upsert
# ===============================
batch_size = 500

success_count = 0
error_count = 0

for i in range(0, len(records), batch_size):
    batch = records[i:i+batch_size]

    try:
        response = (
            supabase
            .table("trading_value_ranking")
            .upsert(batch, on_conflict="today,rank_no")
            .execute()
        )

        if hasattr(response, "error") and response.error:
            print(f"エラー: {response.error}")
            error_count += len(batch)
            continue

        success_count += len(batch)

    except Exception as e:
        print(f"例外エラー: {e}")
        error_count += len(batch)
        continue

    print(f"進捗: {min(i + batch_size, len(records))} / {len(records)}")

# ===============================
# 最終レポート
# ===============================
print("================================")
print(f"CSV件数              : {len(records)}")
print(f"フィルタ前件数        : {df_before_filter}")
print(f"フィルタ後件数        : {df_after_filter}")
print(f"成功件数              : {success_count}")
print(f"失敗件数              : {error_count}")
print("================================")
