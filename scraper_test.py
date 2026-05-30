# =========================
# 制御py（最小構成）
# =========================
from check_update import (
    check_update,
    update_last
)


# =========================
# main
# =========================
def main():

    print("\n===== scraper.py START =====\n")

    # =========================
    # 更新チェックのみ実行
    # =========================
    if not check_update():
        print("[STOP] 変更なし → 全処理停止")
        print("[ABORT] scraper.py 終了")
        return

    # =========================
    # 更新ありのみ last 更新
    # =========================
    try:
        update_last()
        print("[INFO] last_data20.csv 更新完了")

    except Exception as e:
        print(f"[ERROR] update_last失敗: {e}")
        return

    print("\n===== scraper.py END =====\n")
    print("[DONE] check + update_last 完了")


if __name__ == "__main__":
    main()
