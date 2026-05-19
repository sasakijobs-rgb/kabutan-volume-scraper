import os
import csv
import requests
import pandas as pd
from datetime import datetime

# =========================
# 設定
# =========================
FOLDER = "output"
os.makedirs(FOLDER, exist_ok=True)

today = datetime.now().strftime("%Y%m%d")
csv_path = os.path.join(FOLDER, f"trading_value_ranking_{today}.csv")
merged_path = os.path.join(FOLDER, "trading_value_ranking_merged.csv")

log_file = os.path.join(FOLDER, "trading_value_ranking.log")

def log(msg):
    t = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{t} {msg}")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"{t} {msg}\n")


# =========================
# J-Quants API設定
# =========================
API_BASE = "https://api.jquants.com/v1"
REFRESH_URL = f"{API_BASE}/token/auth_refresh"

# GitHub Actionsでは環境変数で管理推奨
REFRESH_TOKEN = os.getenv("JQUANTS_REFRESH_TOKEN")

if not REFRESH_TOKEN:
    raise Exception("JQUANTS_REFRESH_TOKEN が設定されていません")


# =========================
# トークン取得
# =========================
def get_id_token():
    res = requests.post(REFRESH_URL, json={"refreshtoken": REFRESH_TOKEN})
    res.raise_for_status()
    return res.json()["idToken"]


# =========================
# 銘柄一覧取得
# =========================
def get_listed_info(id_token):
    url = f"{API_BASE}/listed/info"
    headers = {"Authorization": f"Bearer {id_token}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()["info"]


# =========================
# 株価取得
# =========================
def get_prices(id_token):
    url = f"{API_BASE}/prices/daily_quotes"
    headers = {"Authorization": f"Bearer {id_token}"}
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.json()["daily_quotes"]


# =========================
# 実行
# =========================
log("開始")

id_token = get_id_token()

listed = get_listed_info(id_token)
prices = get_prices(id_token)

log(f"銘柄数: {len(listed)}")
log(f"価格データ: {len(prices)}")


# =========================
# データ整形
# =========================
df_listed = pd.DataFrame(listed)
df_prices = pd.DataFrame(prices)

# コード統一
df_listed["Code"] = df_listed["Code"].astype(str)
df_prices["Code"] = df_prices["Code"].astype(str)

df = pd.merge(df_prices, df_listed, on="Code", how="left")

# =========================
# 売買代金計算
# =========================
df["TradingValue"] = df["Close"].astype(float) * df["Volume"].astype(float)

# =========================
# ランキング生成
# =========================
df = df.sort_values("TradingValue", ascending=False)

df = df.head(200)  # ← 元の200件運用に戻す

# =========================
# CSV出力（旧フォーマット維持）
# =========================
with open(csv_path, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)

    w.writerow([
        "No","コード","銘柄名","市場","株価",
        "前日比","前日比(%)","売買代金",
        "PER","PBR","利回り"
    ])

    rank = 1

    for _, row in df.iterrows():

        w.writerow([
            rank,
            row.get("Code", ""),
            row.get("CompanyName", ""),
            row.get("MarketCode", ""),
            row.get("Close", ""),
            row.get("ChangePrice", ""),
            row.get("ChangeRatio", ""),
            row.get("TradingValue", ""),
            row.get("PER", ""),
            row.get("PBR", ""),
            row.get("DividendYield", "")
        ])

        rank += 1

log(f"CSV出力完了: {csv_path}")


# =========================
# merge（旧仕様維持）
# =========================
try:
    if os.path.exists(merged_path):
        old = pd.read_csv(merged_path)
    else:
        old = pd.DataFrame()

    new = pd.read_csv(csv_path)

    merged = pd.concat([old, new]).drop_duplicates(subset=["コード"])
    merged.to_csv(merged_path, index=False, encoding="utf-8")

    log("マージ完了")

except Exception as e:
    log(f"マージ失敗: {e}")

log("完了")
