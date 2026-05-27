import os
import glob
import re

OUTPUT_DIR = "output"

MERGED_FILE = os.path.join(
    OUTPUT_DIR,
    "trading_value_ranking_merged.csv"
)

# all(全権を上書き)  latest(当日分を追記)
MODE = "all"  # "all" or "latest"
# 上位200件のみ出力
LIMIT_PER_FILE = 200


# =========================================
# 日付抽出
# =========================================
def extract_date(path):
    m = re.search(r"(\d{8})", path)
    return m.group(1) if m else "00000000"


# =========================================
# ファイル取得
# =========================================
def get_target_files():
    files = glob.glob(os.path.join(OUTPUT_DIR, "*.csv"))
    files = [f for f in files if "merged" not in f]
    files.sort(key=extract_date)
    return files


# =========================================
# ファイル読み込み（★完全テキスト）
# =========================================
def load_from_files(files):
    header = None
    all_lines = []

    for file in files:
        with open(file, "r", encoding="utf-8-sig") as f:

            lines = f.readlines()

            if not lines:
                continue

            # ヘッダー取得（1回だけ）
            if header is None:
                header = lines[0].rstrip("\n")

            # 2行目以降（データのみ）
            data_lines = lines[1:LIMIT_PER_FILE + 1]

            for line in data_lines:
                line = line.strip()
                if line:
                    all_lines.append(line)

    return header, all_lines


# =========================================
# 出力（上書き）
# =========================================
def write_all(header, lines):
    with open(MERGED_FILE, "w", encoding="utf-8-sig") as f:
        if header:
            f.write(header + "\n")

        for line in lines:
            f.write(line + "\n")


# =========================================
# 追記
# =========================================
def append_lines(lines):
    with open(MERGED_FILE, "a", encoding="utf-8-sig") as f:
        for line in lines:
            f.write(line + "\n")


# =========================================
# main
# =========================================
def run():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    files = get_target_files()

    if not files:
        print("[WARN] CSVなし")
        return

    if MODE == "latest":
        files = [files[-1]]

    print(f"[INFO] MODE={MODE}, files={len(files)}")

    header, lines = load_from_files(files)

    if MODE == "all":
        write_all(header, lines)
        print(f"[OK] all再生成: {len(lines)} 行")

    elif MODE == "latest":
        append_lines(lines)
        print(f"[OK] latest追記: {len(lines)} 行")


if __name__ == "__main__":
    run()
