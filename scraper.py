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
import time

OUTPUT_DIR = "output"


def log(msg):
    print(msg)


# =========================
# 共通実行関数（重要）
# =========================
def run_py(name):
    print("\n" + "=" * 50)
    print(f"[RUN START] {name}")
    print("=" * 50)

    start = time.time()

    result = subprocess.run(
        ["python", name],
        capture_output=True,
        text=True
    )

    # 標準出力
    if result.stdout:
        print(result.stdout)

    # エラー表示
    if result.stderr:
        print("\n[ERROR]")
        print(result.stderr)

    end = time.time()

    print("=" * 50)
    print(f"[RUN END] {name}")
    print(f"[TIME] {round(end - start, 2)} sec")
    print("=" * 50 + "\n")

    # エラー時停止
    if result.returncode != 0:
        print(f"[FAILED] {name}")
        exit(1)


# =========================
# メインフロー
# =========================
def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("\n===== PIPELINE START =====\n")

    # =========================
    # STEP 1: cleanup
    # =========================
    print("[STEP 1/3] cleanup.py 実行")
    run_py("cleanup.py")

    # =========================
    # STEP 2: データ取得
    # =========================
    print("[STEP 2/3] data2csv.py 実行")
    run_py("data2csv.py")

    # =========================
    # STEP 3: merge
    # =========================
    print("[STEP 3/3] merge.py 実行")
    run_py("merge.py")

    print("\n===== PIPELINE END =====\n")


if __name__ == "__main__":
    main()
