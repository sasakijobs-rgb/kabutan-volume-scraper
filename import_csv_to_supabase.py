import pandas as pd
import datetime

csv_path = "output/trading_value_ranking_20260530.csv"
print(f"読み込むCSV: {csv_path}")

df = pd.read_csv(csv_path)

# =========================
# 日本語 → 英語カラム
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
# 日付処理（YYYYMMDD前提）
# =========================
df["ymd"] = df["ymd"].astype(str)

# 念のため8桁チェック
df = df[df["ymd"].str.len() == 8]

print("=== 日付デバッグ ===")
print("例:", df["ymd"].head().tolist())

# =========================
# フィルタ（YYYYMMDDのまま比較）
# =========================
target_date = datetime.date.today().strftime("%Y%m%d")

mask = df["ymd"] == target_date
passed = df[mask]
failed = df[~mask]

print("================================")
print(f"TARGET DATE    : {target_date}")
print(f"CSV件数        : {len(df)}")
print(f"フィルタ後件数  : {len(passed)}")
print(f"除外件数        : {len(failed)}")
print("================================")

# =========================
# テスト用：1件で原因表示して停止
# =========================
if len(failed) > 0:
    print("\n=== 除外サンプル（1件） ===")
    row = failed.iloc[0]

    for col in df.columns:
        print(f"{col}: {row[col]}")

    print("\n=== 追加診断 ===")
    print("unique dates sample:", df["ymd"].unique()[:10])

    raise SystemExit("❌ フィルタ不一致のため停止")

print("✔ 正常終了")
