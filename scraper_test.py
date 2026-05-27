# =========================
# 制御pyてすと用(ここから他pyを実行する)
# scraper_test.py
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

    print("\n===== scraper_test.py START =====\n")

    # STEP 1
    print("[STEP 1/1] merge.py 実行")
    #
    if not run_py("merge.py"):
    
        print("[ABORT] merge.py 失敗")
    
        return

    print("\n===== scraper_test.py END =====\n")

    print("[DONE] 全処理成功")


if __name__ == "__main__":
    main()
