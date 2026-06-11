# =========================
# 制御py(ここから他pyを実行する)
# scraper.py
# →last_data20.csvと今回の１ページ目を比較して重複は中止）主に土日祝は中止
# →cleanup.py
# (ファイルが150個以上は削除)
# →data2csv.py
# (株探のモバイル版からデータを取得）
#  →last_data20.csvを更新(data2csvが正常終了時のみ)
# →nikkei_vi_data.csvを更新
# →nikkei_avg_data.csvを更新
# →supabaseへcsvを反映する
# =========================
import os
import subprocess
from check_update import check_update, update_last

# =========================================
# subprocess実行
# =========================================
def run_py(script_name: str) -> bool:

    try:
        result = subprocess.run(
            ["python", script_name],
            check=False
        )

        if result.returncode != 0:
            print(f"[WARN] {script_name} 終了コード: {result.returncode}")
            return False

        return True

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

    # skip判定
    if os.path.exists("output/skip.flag"):
        print("[SKIP] 更新なしフラグ検出 → scraper停止")
        return
        
    # =========================
    # 更新チェック
    # =========================
    if not check_update():
        print("[STOP] 変更なし → 全処理停止")
        return
    try:
        # =========================
        # STEP 1
        # =========================
        print("[STEP 1/4] cleanup.py 実行")

        if not run_py("cleanup.py"):
            print("[ABORT] cleanup失敗")
            return


        # =========================
        # STEP 2
        # =========================
        #print("[STEP 2/4] data2csv.py 実行")

        #if not run_py("data2csv.py"):
        #    print("[ABORT] data2csv失敗")
        #    return
        #print("[STEP 2.5] last_data20.csv 更新（正常終了）")
        #update_last()

        # =========================
        # STEP 3
        # =========================
        print("[STEP 3/4] nikkei_vi_data.py 実行")

        if not run_py("nikkei_vi_data.py"):
           print("[WARN] nikkei_vi_data.py失敗（継続）")

        # =========================
        # STEP 3.5
        # =========================
        print("[STEP 3.5/5] nikkei_avg_data.py 実行")

        if not run_py("nikkei_avg_data.py"):
            print("[WARN] nikkei_avg_data.py失敗（継続）")

        # =========================
        # STEP 4
        # =========================
        print("[STEP 4/4] import_csv_to_supabase.py 実行")

        if not run_py("import_csv_to_supabase.py"):
            print("[WARN] Supabase反映失敗（継続）")

    except Exception as e:
        print(f"[ERROR] {e}")

    finally:
        print("\n===== scraper.py END =====\n")
        print("[DONE] 全処理終了")

if __name__ == "__main__":
    main()
