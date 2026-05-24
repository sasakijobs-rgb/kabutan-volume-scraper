# =========================
# 制御py(ここから他pyを実行する)
# scraper.py
# →last_data20.csvとtoday_data20.csvを比べる
# (この２ファイルが同じなら全ての処理を停止する)
# (前回・今回の１ページ目の内容を出力して比較する）
# →cleanup.py
# (ファイルが150個以上は削除)
# →data2csv.py
# (株探のモバイル版からデータを取得）
# →merge.py
# (最初だけ見出しをセット＆２ファイル目以降はデータのみ)
# →last_data20.csvを更新
# (正常終了時のみlast～は更新されます)
# =========================
import subprocess
from check_update import (
    is_updated,
    update_last
)


# =========================================
# subprocess実行
# =========================================
def run_py(script_name: str) -> bool:

    try:

        result = subprocess.run(
            ["python", script_name],
            check=False
        )

        return result.returncode == 0

    except Exception as e:

        print(
            f"[ERROR] "
            f"{script_name} "
            f"実行失敗: {e}"
        )

        return False


# =========================================
# main
# =========================================
def main():

    print("\n===== scraper.py START =====\n")

    # 更新チェック
    if not is_updated():

        print("[ABORT] scraper.py 終了")

        return

    # STEP 1
    print("[STEP 1/3] cleanup.py 実行")
    #
    if not run_py("cleanup.py"):
    
        print("[ABORT] cleanup失敗")
    
        return

    # STEP 2
    print("[STEP 2/3] data2csv.py 実行")
    
    if not run_py("data2csv.py"):
    
        print("[ABORT] data2csv失敗")
    
        return

    # STEP 3
    print("[STEP 3/3] merge.py 実行")

    if not run_py("merge.py"):

        print("[ABORT] merge失敗")

        return

    # 全成功時のみ更新
    update_last()

    print("\n===== scraper.py END =====\n")

    print("[DONE] 全処理成功")


if __name__ == "__main__":
    main()
