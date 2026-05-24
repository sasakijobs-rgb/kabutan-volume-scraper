import os
import csv
import glob
import shutil

OUTPUT_DIR = "output"

MERGED_FILE = os.path.join(
    OUTPUT_DIR,
    "trading_value_ranking_merged.csv"
)


# =========================================
# 最新CSV取得
# =========================================
def get_latest_csv():
    files = sorted(
        glob.glob(os.path.join(
            OUTPUT_DIR,
            "trading_value_ranking_*.csv"
        ))
    )
    return files[-1] if files else None


# =========================================
# mergedの既存キー読み込み（重複防止）
# =========================================
def load_existing_keys():

    keys = set()

    if not os.path.exists(MERGED_FILE):
        return keys

    with open(MERGED_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        next(reader, None)  # header skip

        for row in reader:
            if len(row) < 4:
                continue

            # 日付 + コードでユニーク化
            keys.add((row[0], row[3]))

    return keys


# =========================================
# 初回作成
# =========================================
def init_merged(latest_csv):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 初回はそのままコピー（最も安全）
    shutil.copy(latest_csv, MERGED_FILE)

    print("[INIT] merged作成完了（初回コピー）")


# =========================================
# 追記処理
# =========================================
def append_to_merged(latest_csv):

    existing = load_existing_keys()
    added = 0

    with open(latest_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        header = next(reader, None)

        with open(MERGED_FILE, "a", newline="", encoding="utf-8-sig") as out:
            writer = csv.writer(out)

            for row in reader:

                if len(row) < 4:
                    continue

                key = (row[0], row[3])

                if key in existing:
                    continue

                writer.writerow(row)
                existing.add(key)
                added += 1

    print(f"[OK] merge完了 +{added}件")


# =========================================
# main
# =========================================
def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    latest_csv = get_latest_csv()

    if not latest_csv:
        print("[WARN] CSVなし")
        return

    # 初回
    if not os.path.exists(MERGED_FILE):
        init_merged(latest_csv)
        return

    # 2回目以降
    append_to_merged(latest_csv)


if __name__ == "__main__":
    run()
