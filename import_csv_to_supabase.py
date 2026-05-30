import pandas as pd

csv_path = "output/trading_value_ranking_20260530.csv"
print(f"読み込むCSV: {csv_path}")

df = pd.read_csv(csv_path)

# =========================
# 日本語 → 英語カラム変換
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
# 数値クリーニング
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
# 日付（そのまま保持・チェックのみ）
# =========================
df["ymd"] = df["ymd"].astype(str)

print("=== 日付サンプル ===")
print(df["ymd"].head().tolist())
print("ユニーク数:", df["ymd"].nunique())

# =========================
# ❌ フィルタなし（ここが重要）
# =========================
passed = df

print("================================")
print(f"CSV件数        : {len(df)}")
print(f"処理対象件数    : {len(passed)}")
print("================================")

# =========================
# テスト用（1件確認）
# =========================
print("\n=== サンプル1件 ===")
print(passed.iloc[0].to_dict())

print("✔ フィルタなしで正常終了")
