import pandas as pd
import datetime

csv_path = "output/trading_value_ranking_20260530.csv"
print(f"読み込むCSV: {csv_path}")

df = pd.read_csv(csv_path)

# =========================
# 日本語 → DB用英語カラム
# =========================
df = df.rename(columns={
    "日付": "ymd",
    "順位": "rank",
    "銘柄名": "name",
    "コード": "code",
    "市場": "market",
    "状態": "status",
    "株価": "stock_price",
    "前日差": "diff_price",
    "騰落率": "diff_percent",
    "売買代金": "trade_volume",
    "PER": "per",
    "PBR": "pbr",
    "配当利回り": "yld",
})

# =========================
# 日付変換
# =========================
df["ymd"] = pd.to_datetime(df["ymd"], errors="coerce").dt.date

print("=== 正規化後カラム ===")
print(df.columns.tolist())

print("=== 日付デバッグ ===")
print("NaT件数:", df["ymd"].isna().sum())
print("例:", df["ymd"].head().tolist())

# =========================
# フィルタ（必要なら）
# =========================
target_date = datetime.date.today()

mask = df["ymd"] == target_date
passed = df[mask]
failed = df[~mask]

print("================================")
print(f"CSV件数        : {len(df)}")
print(f"フィルタ後件数  : {len(passed)}")
print(f"除外件数        : {len(failed)}")
print("================================")

# =========================
# テスト用：1件で停止
# =========================
if len(failed) > 0:
    print("\n=== 除外サンプル（1件） ===")
    row = failed.iloc[0]

    for col in df.columns:
        print(f"{col}: {row[col]}")

    raise SystemExit("❌ フィルタ不一致のため停止")

print("✔ 正常終了")
