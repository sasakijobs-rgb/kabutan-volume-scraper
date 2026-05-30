import pandas as pd

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
# 数値クリーニング（カンマ除去）
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
# 文字列として保持（YYYYMMDD）
# =========================
df["ymd"] = df["ymd"].astype(str)

print("=== 日付サンプル ===")
print(df["ymd"].head().tolist())
print("ユニーク数:", df["ymd"].nunique())

# =========================
# フィルタ（必要なら使用）
# ※今は全件通す想定
# =========================
passed = df

print("================================")
print(f"CSV件数        : {len(df)}")
print(f"処理対象件数    : {len(passed)}")
print("================================")

# =========================
# DB投入直前で date型へ変換
# =========================
passed["ymd"] = pd.to_datetime(
    passed["ymd"],
    format="%Y%m%d",
    errors="coerce"
).dt.date

# =========================
# 変換チェック（安全策）
# =========================
if passed["ymd"].isna().any():
    print("❌ 日付変換失敗あり（停止）")
    print(passed[passed["ymd"].isna()].head())
    raise SystemExit()

# =========================
# サンプル表示
# =========================
print("\n=== サンプル1件 ===")
print(passed.iloc[0].to_dict())

# =========================
# Supabase用データ化
# =========================
records = passed.to_dict(orient="records")

print("\n✔ 変換完了（Supabase投入準備OK）")
