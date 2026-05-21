import os

OUTPUT_DIR = "output"
MAX_FILES = 150


def log(msg):
    print(msg)


def get_target_files():

    files = [
        f for f in os.listdir(OUTPUT_DIR)
        if f.startswith("trading_value_ranking_")
        and f.endswith(".csv")
        and f != "trading_value_ranking_merged.csv"
    ]

    files.sort()
    return files


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

        file_path = os.path.join(OUTPUT_DIR, files[i])

        try:
            os.remove(file_path)
            log(f"[DELETE] {files[i]}")

        except Exception as e:
            log(f"[ERROR] {files[i]}: {e}")

    log("[DONE] cleanup finished")


if __name__ == "__main__":
    cleanup()
