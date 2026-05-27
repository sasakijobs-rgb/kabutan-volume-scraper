import os
import csv
import glob
import shutil
from collections import defaultdict

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
# merged読み込み（既存データ取得）
# =========================================
def load_existing_rows():
    rows = []

    if not os.path.exists(MERGED_FILE):
        return rows

    with open(MERGED_FILE, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)

        header = next(reader, None)

        for row in reader:
            if len(row) < 4:
                continue
            rows.append(row)

    return rows


# =========================================
# 初回作成
# =========================================
def init_merged(latest_csv):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    shutil.copy(latest_csv, MERGED_FILE)
    print("[INIT] merged作成完了（初回コピー）")


# =========================================
# 日別200件制限 + マージ再構築
# =========================================
def rebuild_merged(latest_csv):

    existing_rows = load_existing_rows()
    new_rows = []

    # 最新CSV読み込み
    with open(latest_csv, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        for row in reader:
            if len(row) < 4:
                continue
            existing_rows.append(row)

    # =====================================
    # 重複排除（date + code）
    # =====================================
    seen_keys = set()
    deduped = []

    for row in existing_rows:
        key = (row[0], row[3])
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(row)

    # =====================================
    # 日別グルーピング
    # =====================================
    grouped = defaultdict(list)

    for row in deduped:
        date = row[0]
        grouped[date].append(row)

    # =====================================
    # 日別200件制限
    # =====================================
    final_rows = []

    for date, rows in grouped.items():
        final_rows.extend(rows[:200])

    # =====================================
    # 書き直し（上書き）
    # =====================================
    with open(MERGED_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if header:
            writer.writerow(header)

        writer.writerows(final_rows)

    print(f"[OK] merge完了（日別200件制限） 総件数: {len(final_rows)}")


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

    # 2回目以降は再構築
    rebuild_merged(latest_csv)


if __name__ == "__main__":
    run()
