# =========================
# 制御py(ここから他pyを実行する)
# scraper.py
# (１ページが前回の内容と同じなら中断）
# →cleanup.py
# (ファイルが150個以上は削除)
# →data2csv.py
# (株探のモバイル版からデータを取得）
# →merge.py
# (最初だけ見出しをセット＆２ファイル目以降はデータのみ)
# =========================

import os
import subprocess
import hashlib

OUTPUT_DIR = "output"
HASH_FILE = os.path.join(OUTPUT_DIR, ".page1_hash")


def log(msg):
    print(msg)


# =========================
# 最新CSV取得（＝比較対象）
# =========================
def get_latest_file():

    files = [
        f for f in os.listdir(OUTPUT_DIR)
        if f.startswith("trading_value_ranking_")
        and f.endswith(".csv")
        and f != "trading_value_ranking_merged.csv"
    ]

    if not files:
        return None

    files.sort()
    return os.path.join(OUTPUT_DIR, files[-1])


# =========================
# ハッシュ取得
# =========================
def get_hash(path):

    if not path or not os.path.exists(path):
        return None

    with open(path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def load_old_hash():

    if not os.path.exists(HASH_FILE):
        return None

    with open(HASH_FILE, "r") as f:
        return f.read().strip()


def save_hash(h):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(HASH_FILE, "w") as f:
        f.write(h)


# =========================
# cleanup実行
# =========================
def run_cleanup():

    log("[STEP] cleanup start")

    subprocess.run(["python", "cleanup.py"], check=True)


# =========================
# data2csv実行
# =========================
def run_scraper():

    log("[STEP] data2csv start")

    subprocess.run(["python", "data2csv.py"], check=True)


# =========================
# merge実行
# =========================
def run_merge():

    log("[STEP] merge start")

    subprocess.run(["python", "merge.py"], check=True)


# =========================
# メインフロー
# =========================
def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    log("===== PIPELINE START =====")

    # =========================
    # STEP1: 更新チェック
    # =========================
    latest_file = get_latest_file()
    new_hash = get_hash(latest_file)
    old_hash = load_old_hash()

    if new_hash and new_hash == old_hash:

        log("[SKIP] no update detected (same data)")
        log("===== STOP =====")
        return

    save_hash(new_hash)

    log("[INFO] data changed -> continue pipeline")

    # =========================
    # STEP2: cleanup
    # =========================
    run_cleanup()

    # =========================
    # STEP3: data2csv
    # =========================
    run_scraper()

    # =========================
    # STEP4: merge
    # =========================
    run_merge()

    log("===== PIPELINE END =====")


if __name__ == "__main__":
    main()
