# =========================
# 制御py（Supabaseテスト専用）
# scraper_test.py
# →import_csv_to_supabase.pyのみ実行
# =========================

import subprocess


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
            print(f"[ERROR] {script_name} 終了コード: {result.returncode}")
            return False

        return True

    except Exception as e:
        print(f"[ERROR] {script_name} 実行失敗: {e}")
        return False


# =========================================
# main
# =========================================
def main():

    print("\n===== scraper_test.py START =====\n")

    print("[STEP] import_csv_to_supabase.py 実行")

    if not run_py("import_csv_to_supabase.py"):
        print("[ABORT] Supabase実行失敗")
        return

    print("\n===== scraper_test.py END =====\n")
    print("[DONE] Supabase実行成功")


if __name__ == "__main__":
    main()
