import os
import pandas as pd
from datetime import datetime
from supabase import create_client
import sys

# ===============================
# Supabase設定（GitHub ActionsならSecrets経由）
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

# 空文字やNaNをNoneに変換
df = df.where(pd.notnull(df), None)

# 型変換
if "rank_no" in df.columns:
    df["rank_no"] = df["rank_no"].astype("Int64")

if "trade_value" in df.columns:
    df["trade_value"] = df["trade_value"].astype("Int64")

for col in ["stock_price", "diff_price", "diff_percent", "per", "pbr", "yld"]:
    if col in df.columns:
        df[col] = df[col].apply(lambda x: float(x) if x is not None else None)

# ===============================
# Supabase用に辞書化
# ===============================
records = df.to_dict(orient="records")

# ===============================
# バッチでINSERT（安全のため500件ごと）
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
