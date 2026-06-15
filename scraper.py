import sys
import subprocess

from check_update import check_update, update_last


# =========================
# 実行フラグ（ここだけ見れば制御が分かる）
# =========================
RUN_CLEANUP = True
RUN_NIKKEI_VI = True
RUN_NIKKEI_AVG = True
RUN_CSV_TRADING_VALUE = True
RUN_DB_STOCK_REPORTS = True
RUN_DB_TRADING_VALUE = True

# =========================
# subprocess実行
# =========================
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
        print(f"[ERROR] {script_name} 実行失敗: {e}")
        return False


# =========================
# 各ステップ
# =========================
def step_cleanup():
    return run_py("cleanup.py")

def step_nikkei_vi():
    return run_py("nikkei_vi_data.py")

def step_nikkei_avg():
    return run_py("nikkei_avg_data.py")

def step_csv_trading_value():
    return run_py("CSV_trading_value.py")

def step_db_stock_reports():
    return run_py("DB_stock_reports.py")

def step_db_trading_value():
    return run_py("DB_trading_value.py")

# =========================
# フル実行
# =========================
def run_full():

    print("\n===== FULL RUN START =====\n")

    # 更新チェック（差分なしなら完全停止）
    if not check_update():
        print("[STOP] 変更なし → 全処理停止")
        return

    # 1. cleanup
    if RUN_CLEANUP:
        step_cleanup()

    # 2. nikkei vi
    if RUN_NIKKEI_VI:
        step_nikkei_vi()

    # 3. nikkei avg
    if RUN_NIKKEI_AVG:
        step_nikkei_avg()

    # 4. CSV trading value
    if RUN_CSV_TRADING_VALUE:
        ok = step_csv_trading_value()

        if not ok:
            print("[ABORT] CSV_trading_value失敗 → 後続停止")
            return

    # 5. stock reports
    if RUN_DB_STOCK_REPORTS:
        step_db_stock_reports()

    # 6. trading value
    if RUN_DB_TRADING_VALUE:
        step_db_trading_value()
    
    print("\n===== FULL RUN END =====")

    # 成功時のみ last 更新
    update_last()

# =========================
# エントリポイント
# =========================
def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "normal"

    print(f"[MODE] {mode}")

    # 部分実行モード
    if mode == "cleanup":
        step_cleanup()
        return

    if mode == "nikkei_vi":
        step_nikkei_vi()
        return

    if mode == "nikkei_avg":
        step_nikkei_avg()
        return

    if mode == "csv_trading_value":
        step_csv_trading_value()
        return
    
    if mode == "db_stock_reports":
        step_db_stock_reports()
        return

    if mode == "db_trading_value":
        step_db_trading_value()
        return

    # 通常フル実行
    run_full()


if __name__ == "__main__":
    main()
