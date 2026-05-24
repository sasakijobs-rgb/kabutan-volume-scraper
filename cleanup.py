import os
import re

OUTPUT_DIR = "output"
MAX_FILES = 150


def log(msg):
    print(msg)


# =========================================
# 対象ファイル取得
# =========================================
def get_target_files():

    if not os.path.exists(OUTPUT_DIR):

        log("[INFO] output dir not found")

        return []

    # 対象:
    # trading_value_ranking_YYYYMMDD.csv
    pattern = re.compile(
        r"^trading_value_ranking_(\d{8})\.csv$"
    )

    files = []

    for f in os.listdir(OUTPUT_DIR):

        # 除外ファイル
        if f in [
            "today_data20.csv",
            "last_data20.csv",
            "trading_value_ranking_merged.csv"
        ]:
            continue

        # 日付CSVのみ対象
        if pattern.match(f):

            files.append(f)

    # 古い順
    files.sort()

    return files


# =========================================
# cleanup
# =========================================
def cleanup():

    files = get_target_files()

    file_count = len(files)

    log(f"[INFO] current files: {file_count}")

    if file_count <= MAX_FILES:

        log("[OK] cleanup not needed")

        return

    delete_count = file_count - MAX_FILES

    log(f"[INFO] deleting {delete_count} old files")

    for i in range(delete_count):

        file_name = files[i]

        file_path = os.path.join(
            OUTPUT_DIR,
            file_name
        )

        try:

            os.remove(file_path)

            log(f"[DELETE] {file_name}")

        except Exception as e:

            log(f"[ERROR] {file_name}: {e}")

    log("[DONE] cleanup finished")


if __name__ == "__main__":
    cleanup()
