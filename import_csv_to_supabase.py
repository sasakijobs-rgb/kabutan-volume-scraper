import pandas as pd
import datetime

csv_path = "output/trading_value_ranking_20260530.csv"
print(f"読み込むCSV: {csv_path}")

df = pd.read_csv(csv_path)

# =========================
# 日本語 → 英語カラム変換（DB用）
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
# 数値クリーニング（重要）
# =========================
def clean_number(x):
    if pd.isna(x):
        return None
    if isinstance(x, str):
        return x.replace(",", "")
    return x

for col in ["stock_price", "diff_price", "trade_volume"]:
    df[col] = df[col].apply(clean_number)

# =========================
# 日付変換（YYYYMMDD対応）
# =========================
df["ymd"] = pd.to_datetime(
    df["ymd"].astype(str),
    format="%Y%m%d",
    errors="coerce"
).dt.date

# =========================
# 日付デバッグ
# =========================
print("=== 日付デバッグ ===")
print("NaT件数:", df["ymd"].isna().sum())
print("例:", df["ymd"].head().tolist())

if df["ymd"].isna().any():
    print("\n❌ 日付変換失敗データあり（停止）")
    print(df[df["ymd"].isna()].head(5))
    raise SystemExit()

# =========================
# フィルタ
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
# テスト用：1件で停止（原因表示）
# =========================
if len(failed) > 0:
    print("\n=== 除外サンプル（1件） ===")
    row = failed.iloc[0]

    for col in df.columns:
        print(f"{col}: {row[col]}")

    print("\n=== 追加診断 ===")
    print("ymd dtype:", df["ymd"].dtype)
    print("target_date:", target_date)
    print("unique dates sample:", df["ymd"].unique()[:10])

    raise SystemExit("❌ フィルタ不一致のため停止")

# =========================
# 成功
# =========================
print("✔ 正常終了（全件通過）")
