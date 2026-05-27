import os
import csv
import glob
import re

OUTPUT_DIR = "output"

MERGED_FILE = os.path.join(
    OUTPUT_DIR,
    "trading_value_ranking_merged.csv"
)

# =========================================
# MODE設定
# "all" or "latest"
# =========================================
MODE = "all"

LIMIT_PER_FILE = 200


# =========================================
# yyyymmdd抽出
# =========================================
def extract_date(path):
    m = re.search(r"(\d{8})", path)
    return m.group(1) if m else "00000000"


# =========================================
# CSV一覧取得
# =========================================
def get_target_csv_files():
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
    files = [f for f in files if "merged" not in f]
    files.sort(key=extract_date)
    return files


# =========================================
# 重複排除
# =========================================
def deduplicate(rows):
    seen = set()
    result = []

    for row in rows:
        if len(row) < 4:
            continue

        key = (row[0], row[3])
        if key in seen:
            continue

        seen.add(key)
        result.append(row)

    return result


# =========================================
# ファイルから上位200件取得
# =========================================
def load_from_files(files):
    all_rows = []
    header = None

    for file in files:
        with open(file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)

            file_header = next(reader, None)
            if header is None:
                header = file_header

            count = 0

            for row in reader:
                if len(row) < 4:
                    continue

                all_rows.append(row)
                count += 1

                if count >= LIMIT_PER_FILE:
                    break

    return header, all_rows


# =========================================
# 書き込み（上書き）
# =========================================
def write_all(header, rows):
    with open(MERGED_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        if header:
            writer.writerow(header)

        writer.writerows(rows)


# =========================================
# 追記
# =========================================
def append_rows(header, rows):
    file_exists = os.path.exists(MERGED_FILE)

    with open(MERGED_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # 初回のみヘッダー
        if not file_exists and header:
            writer.writerow(header)

        writer.writerows(rows)


# =========================================
# main
# =========================================
def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = get_target_csv_files()

    if not files:
        print("[WARN] CSVなし")
        return

    # 最新 or 全件
    if MODE == "latest":
        files = [files[-1]]

    print(f"[INFO] MODE={MODE}, files={len(files)}")

    header, rows = load_from_files(files)

    # 重複排除
    rows = deduplicate(rows)

    # 出力制御
    if MODE == "all":
        # クリアして再生成
        write_all(header, rows)
        print(f"[OK] 全ファイル再生成: {len(rows)} 件")

    elif MODE == "latest":
        # 追記
        append_rows(header, rows)
        print(f"[OK] 最新ファイル追記: {len(rows)} 件")


if __name__ == "__main__":
    run()
