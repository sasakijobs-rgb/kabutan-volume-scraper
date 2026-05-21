import os
import csv
import hashlib

OUTPUT_DIR = "output"
MERGED_FILE = "output/trading_value_ranking_merged.csv"
HASH_FILE = "output/.merge_hash"


def log(msg):
    print(msg)


def get_csv_files():

    files = [
        f for f in os.listdir(OUTPUT_DIR)
        if f.startswith("trading_value_ranking_")
        and f.endswith(".csv")
        and f != "trading_value_ranking_merged.csv"
    ]

    files.sort()
    return files


def calc_hash(files):

    h = hashlib.md5()

    for f in files:

        path = os.path.join(OUTPUT_DIR, f)

        with open(path, "rb") as fp:
            h.update(fp.read())

    return h.hexdigest()


def load_hash():

    if not os.path.exists(HASH_FILE):
        return None

    with open(HASH_FILE, "r") as f:
        return f.read().strip()


def save_hash(h):

    with open(HASH_FILE, "w") as f:
        f.write(h)


def merge():

    files = get_csv_files()

    if not files:
        log("[SKIP] no csv files found")
        return

    new_hash = calc_hash(files)
    old_hash = load_hash()

    if new_hash == old_hash:
        log("[SKIP] no changes detected")
        return

    merged_rows = []
    header = None

    for file in files:

        path = os.path.join(OUTPUT_DIR, file)

        with open(path, "r", encoding="utf-8-sig") as f:

            reader = list(csv.reader(f))

            if not reader:
                continue

            if header is None:
                header = reader[0]

            merged_rows.extend(reader[1:])  # ヘッダー除外

    with open(MERGED_FILE, "w", newline="", encoding="utf-8-sig") as f:

        writer = csv.writer(f)

        if header:
            writer.writerow(header)

        writer.writerows(merged_rows)

    save_hash(new_hash)

    log(f"[MERGED] {len(merged_rows)} rows")
    log(f"[FILE] {MERGED_FILE}")


if __name__ == "__main__":
    merge()
