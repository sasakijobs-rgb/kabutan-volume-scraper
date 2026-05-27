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
# =========================================
# "all(全件を上書き") or "latest(最新日のみ追記)"
MODE = "all"
# 上位200件のみ出力する
LIMIT_PER_FILE = 200


# =========================================
# 日付抽出
# =========================================
def extract_date(path):
    m = re.search(r"(\d{8})", path)
    return m.group(1) if m else "00000000"


# =========================================
# CSV取得
# =========================================
def get_target_csv_files():
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
    files = [f for f in files if "merged" not in f]
    files.sort(key=extract_date)
    return files


# =========================================
# ファイル読み込み（★2行目以降のみ）
# =========================================
def load_from_files(files):
    all_rows = []
    header = None

    for file in files:
        with open(file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)

            file_header = next(reader, None)
            if header is None:
                header = file_header  # 1回だけ保持

            count = 0

            for row in reader:  # ★ここで既に2行目以降
                if not row:
                    continue

                # 行の最低チェック
                if len(row) < 5:
                    continue

                all_rows.append(row)
                count += 1

                if count >= LIMIT_PER_FILE:
                    break

    return header, all_rows


# =========================================
# 重複排除（date + code）
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
# 上書き出力（all）
# =========================================
def write_all(header, rows):
    with open(MERGED_FILE, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        # ★ヘッダーは1回だけ
        if header:
            writer.writerow(header)

        writer.writerows(rows)


# =========================================
# 追記（latest）
# =========================================
def append_rows(rows):
    file_exists = os.path.exists(MERGED_FILE)

    with open(MERGED_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)

        writer.writerows(rows)  # ★ヘッダーは書かない


# =========================================
# main
# =========================================
def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = get_target_csv_files()

    if not files:
        print("[WARN] CSVなし")
        return

    # latestなら1ファイルのみ
    if MODE == "latest":
        files = [files[-1]]

    print(f"[INFO] MODE={MODE}, files={len(files)}")

    header, rows = load_from_files(files)

    rows = deduplicate(rows)

    # =========================================
    # 出力制御
    # =========================================
    if MODE == "all":
        # ★完全再生成
        write_all(header, rows)
        print(f"[OK] all再生成: {len(rows)} 件")

    elif MODE == "latest":
        # ★追記（2行目以降のみ）
        append_rows(rows)
        print(f"[OK] latest追記: {len(rows)} 件")


if __name__ == "__main__":
    run()
