import pandas as pd
import glob
import os
import sys
from datetime import datetime

# =====================================
# 実行パラメータ
# python merge.py all
# python merge.py today
# =====================================
# sw = "all"
sw = "today"

# 1ファイルあたり最大読込件数
MAX_ROWS = 200

# =====================================
# 設定
# =====================================

input_pattern = "output/trading_value_ranking_2*.csv"
output_file = "output/trading_value_ranking_merged.csv"

headers = [
    "日付",
    "順位",
    "銘柄名",
    "コード",
    "市場",
    "状態",
    "株価",
    "前日差",
    "騰落率",
    "売買代金",
    "PER",
    "PBR",
    "配当利回り"
]

# =====================================
# 出力フォルダ作成
# =====================================

os.makedirs("output", exist_ok=True)

# =====================================
# 対象ファイル取得
# =====================================

files = sorted(glob.glob(input_pattern))

# マージ済みファイル除外
files = [
    f for f in files
    if os.path.basename(f) != "trading_value_ranking_merged.csv"
]

# =====================================
# 出力ファイル存在確認
# =====================================

if not os.path.exists(output_file):

    empty_df = pd.DataFrame(columns=headers)

    empty_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    print(f"新規作成: {output_file}")

# =====================================
# all
# 全件再構築
# =====================================

if sw == "all":

    print("全件再構築開始")

    # 初期化（見出しのみ）
    empty_df = pd.DataFrame(columns=headers)

    empty_df.to_csv(
        output_file,
        index=False,
        encoding="utf-8-sig"
    )

    for file in files:

        try:

            df = pd.read_csv(
                file,
                skiprows=1,
                header=None,
                nrows=MAX_ROWS,
                encoding="utf-8-sig"
            )

            # 空ファイル対策
            if df.empty:
                print(f"空ファイル: {file}")
                continue

            df.columns = headers

            df.to_csv(
                output_file,
                mode="a",
                header=False,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"追加: {file} ({len(df)}件)")

        except Exception as e:
            print(f"エラー: {file} : {e}")

# =====================================
# today
# 当日ファイルのみ追記
# =====================================

elif sw == "today":

    today = datetime.now().strftime("%Y%m%d")

    today_file = f"output/trading_value_ranking_{today}.csv"

    if os.path.exists(today_file):

        try:

            df = pd.read_csv(
                today_file,
                skiprows=1,
                header=None,
                nrows=MAX_ROWS,
                encoding="utf-8-sig"
            )

            # 空ファイル対策
            if df.empty:
                print(f"空ファイル: {today_file}")
                sys.exit(0)

            df.columns = headers

            df.to_csv(
                output_file,
                mode="a",
                header=False,
                index=False,
                encoding="utf-8-sig"
            )

            print(f"当日追記: {today_file} ({len(df)}件)")

        except Exception as e:
            print(f"エラー: {today_file} : {e}")

    else:
        print(f"当日ファイルなし: {today_file}")

# =====================================
# 不正パラメータ
# =====================================

else:
    print("sw は all または today を指定してください")
