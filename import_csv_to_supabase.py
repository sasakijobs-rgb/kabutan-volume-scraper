import os
import pandas as pd
import numpy as np
from datetime import datetime
from supabase import create_client
import sys

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
# 当日CSVファイルパス
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
# 数値クリーニング関数
# ===============================
def to_number(x):
    if x is None:
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
# 数値列変換（安全化）
# ===============================
numeric_cols = ["株価", "前日差", "騰落率", "売買代金", "PER", "PBR", "配当利回り"]

for col in numeric_cols:
    if col in df.columns:
        df[col] = df[col].apply(to_number)

# rank / code系（整数）
if "順位" in df.columns:
    df["順位"] = pd.to_numeric(df["順位"], errors="coerce").astype("Int64")

if "コード" in df.columns:
    df["コード"] = df["コード"].astype(str)

# ===============================
# NaN / inf 完全除去（重要）
# ===============================
df = df.replace([np.inf, -np.inf], np.nan)
df = df.where(pd.notnull(df), None)

# ===============================
# Supabase用に辞書化
# ===============================
records = df.to_dict(orient="records")

# ===============================
# バッチINSERT
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
