import pandas as pd
import datetime

# CSV読み込み
csv_path = "output/trading_value_ranking_20260530.csv"
print(f"読み込むCSV: {csv_path}")

df = pd.read_csv(csv_path)

# もし日付列がある想定（必要なら変更）
date_col = "date"

# 日付型を統一（重要）
df[date_col] = pd.to_datetime(df[date_col], errors="coerce").dt.date

print("=== 日付デバッグ ===")
print("NaT件数:", df[date_col].isna().sum())
print("例:", df[date_col].head().tolist())
print("================================")

target_date = datetime.date.today()

# ===== フィルタ =====
mask = df[date_col] == target_date

passed = df[mask]
failed = df[~mask]

print("=== フィルタ結果 ===")
print(f"target_date        : {target_date}")
print(f"CSV件数            : {len(df)}")
print(f"フィルタ前件数      : {len(df)}")
print(f"フィルタ後件数      : {len(passed)}")
print(f"除外件数            : {len(failed)}")
print("================================")

# ===== デバッグ（1件表示して停止）=====
if len(failed) > 0:
    print("\n=== 除外サンプル（1件のみ表示） ===")

    row = failed.iloc[0]

    for col in df.columns:
        print(f"{col}: {row[col]}")

    # 追加診断（かなり重要）
    print("\n=== 追加診断 ===")
    print("date dtype:", df[date_col].dtype)
    print("target_date type:", type(target_date))
    print("sample unique dates:", df[date_col].dropna().unique()[:10])

    raise SystemExit("❌ フィルタ不一致のため停止")

# ===== 成功時 =====
print("✔ フィルタ成功（全件通過）")

# 以降の処理へ
# df = passed
