# =========================
# 制御py(ここから他pyを実行する)
# scraper_test.py
# →last_data20.csvとtoday_data20.csvを比べる
# (この２ファイルが同じなら全ての処理を停止する)
# (前回・今回の１ページ目の内容を出力して比較する）
# →cleanup.py
# (ファイルが150個以上は削除)
# →data2csv.py
# (株探のモバイル版からデータを取得）
# →merge.py
# (最初だけ見出しをセット＆２ファイル目以降はデータのみ)
# →nikkei_data_vi.csvを更新
# →last_data20.csvを更新
# (正常終了時のみlast～は更新されます)
# =========================
# =========================
# 制御py(ここから他pyを実行する)
# scraper_test.py
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
    check_update,
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

    print("\n===== scraper_test.py START =====\n")

    # STEP 2
    print("[STEP 2/4] nikkei_vi_data.py 実行")

    if not run_py("nikkei_vi_data.py"):
        print("[ABORT] nikkei_vi_data.py失敗")
        return


    print("\n===== scraper_test.py END =====\n")
    print("[DONE] 全処理成功")


if __name__ == "__main__":
    main()
