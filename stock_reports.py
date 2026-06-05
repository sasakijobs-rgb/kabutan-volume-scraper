import os
import pandas as pd
import numpy as np
from supabase import create_client

# 既存のスクレイピング部分は df に結果が入っている前提

# =========================
# Supabase接続
# =========================
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
TABLE_NAME = "stock_reports"

# =========================
# 前処理（1ページ目向け簡略版）
# =========================
def preprocess(df: pd.DataFrame) -> pd.DataFrame:

    # カラム名統一
    df = df.rename(columns={
        "銘柄コード": "code",
        "銘柄名": "name",
        "現在株価": "stock_price",
        "レポート公開日": "report_date",
        "発表機関": "broker",
        "レポートタイトル": "title",
        "レーティング": "rating",
        "目標株価": "target_price",
        "目標株価乖離率": "target_gap",
        "取得ページ": "source_page",
    })

    # 数値化
    for col in ["stock_price", "target_price", "target_gap"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 日付変換
    if "report_date" in df.columns:
        df["report_date"] = pd.to_datetime(
            df["report_date"], errors="coerce"
        ).dt.strftime("%Y-%m-%d")

    # Supabase安全化
    df = df.replace([np.nan, np.inf, -np.inf], None)

    # 今日分だけ
    today = pd.Timestamp.today().strftime("%Y-%m-%d")
    df = df[df["report_date"] == today]

    # 重複排除
    df = df.drop_duplicates(subset=["code", "report_date"]).reset_index(drop=True)

    return df

# =========================
# Supabaseに送信
# =========================
def insert(df: pd.DataFrame):
    if df.empty:
        print("[INFO] 本日分データなし")
        return

    batch_size = 500
    records = df.to_dict(orient="records")

    print(f"[INFO] insert: {len(records)} rows")

    for i in range(0, len(records), batch_size):
        batch = records[i:i+batch_size]
        supabase.table(TABLE_NAME).upsert(
            batch,
            on_conflict="code,report_date"
        ).execute()
        print(f"[OK] {min(i+batch_size, len(records))}/{len(records)}")

# =========================
# 実行
# =========================
if __name__ == "__main__":

    # ここに既存スクレイピングコードを入れて df を作成済みとする
    # df = pd.DataFrame(data)  # ← 今のスクレイピング部分

    df = preprocess(df)
    insert(df)
    print("処理完了")
