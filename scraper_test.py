import requests
from bs4 import BeautifulSoup
import json
import os
import subprocess

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all"

OUTPUT_DIR = "output"
TODAY_FILE = os.path.join(OUTPUT_DIR, "today.json")
LAST_FILE = os.path.join(OUTPUT_DIR, "last.json")


# =========================================
# subprocess実行（成功/失敗を返す）
# =========================================
def run_py(script_name: str) -> bool:
    try:
        result = subprocess.run(
            ["python", script_name],
            check=False
        )
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] {script_name} 実行失敗: {e}")
        return False


# =========================================
# HTML取得
# =========================================
def fetch_html():
    try:
        r = requests.get(URL, timeout=30)
        if r.status_code != 200:
            return None
        return r.text
    except Exception:
        return None


# =========================================
# テーブル抽出 → dict化
# =========================================
def extract_table(html):
    if not html:
        return []

    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("table.stock_table.st_market tbody tr")

    data = []

    for row in rows:
        cols = row.find_all(["td", "th"])

        if len(cols) < 10:
            continue

        data.append({
            "code": cols[0].get_text(strip=True),
            "name": cols[1].get_text(strip=True),
            "price": cols[5].get_text(strip=True),
            "change": cols[7].get_text(strip=True),
            "change_percent": cols[8].get_text(strip=True),
        })

    return data


# =========================================
# JSON保存
# =========================================
def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# =========================================
# JSON読み込み
# =========================================
def load_json(path):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# =========================================
# 更新チェック
# =========================================
def is_updated():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    html = fetch_html()
    current = extract_table(html)

    if not current:
        print("[ERROR] データ取得失敗")
        return False

    # 今回データ保存（比較用）
    save_json(TODAY_FILE, current)

    old = load_json(LAST_FILE)

    # 初回
    if old is None:
        print("[INFO] 初回実行（更新扱い）")
        return True

    # 比較
    if old == current:
        print("[STOP] 変更なし → 全処理中断")
        return False

    print("[RUN] 更新あり")
    return True


# =========================================
# main pipeline
# =========================================
def main():

    print("\n===== PIPELINE START =====\n")

    # =========================
    # 事前チェック（変更なしなら全停止）
    # =========================
    if not is_updated():
        print("[ABORT] 変更なしのため終了")
        return

    # =========================
    # STEP 1: cleanup
    # =========================
    print("[STEP 1/3] cleanup.py 実行")
    if not run_py("cleanup.py"):
        print("[ABORT] cleanup失敗")
        return

    # =========================
    # STEP 2: データ取得
    # =========================
    print("[STEP 2/3] data2csv.py 実行")
    if not run_py("data2csv.py"):
        print("[ABORT] data2csv失敗 → last.json 更新なし")
        return

    # =========================
    # STEP 3: merge
    # =========================
    print("[STEP 3/3] merge.py 実行")
    if not run_py("merge.py"):
        print("[ABORT] merge失敗")
        return

    # =========================
    # 全て正常終了時のみlast.jsonを更新
    # =========================
    # 成功時のみ last.json 更新
    print("[INFO] last.json 更新（STEP2成功）")
    today_data = load_json(TODAY_FILE)
    if today_data is not None:
        save_json(LAST_FILE, today_data)


    print("\n===== PIPELINE END =====\n")
    print("[DONE] 全処理成功")


if __name__ == "__main__":
    main()
