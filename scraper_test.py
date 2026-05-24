import requests
from bs4 import BeautifulSoup
import json
import os
import shutil
import sys

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all"

OUTPUT_DIR = "output"

CURRENT_FILE = os.path.join(OUTPUT_DIR, "current.json")
PREVIOUS_FILE = os.path.join(OUTPUT_DIR, "previous.json")


# =========================================
# HTML取得
# =========================================
def fetch_first_page():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/124.0 Safari/537.36"
        )
    }

    try:

        response = requests.get(
            URL,
            headers=headers,
            timeout=30
        )

        response.raise_for_status()

        response.encoding = response.apparent_encoding

        print("[OK] HTML取得成功")

        return response.text

    except Exception as e:

        print(f"[ERROR] HTML取得失敗: {e}")

        return None


# =========================================
# テーブル → dict化
# =========================================
def extract_stock_data(html):

    if not html:
        return None

    try:

        soup = BeautifulSoup(html, "html.parser")

        rows = soup.select("table.stock_table.st_market tbody tr")

        stocks = []

        for row in rows:

            cols = row.find_all(["td", "th"])

            if len(cols) < 13:
                continue

            item = {
                "code": cols[0].get_text(strip=True),
                "name": cols[1].get_text(strip=True),
                "market": cols[2].get_text(strip=True),
                "price": cols[5].get_text(strip=True),
                "change": cols[7].get_text(strip=True),
                "change_percent": cols[8].get_text(strip=True),
                "trading_value": cols[9].get_text(strip=True),
                "per": cols[10].get_text(strip=True),
                "pbr": cols[11].get_text(strip=True),
                "yield": cols[12].get_text(strip=True),
            }

            stocks.append(item)

        # JSONとして安定化（順序固定）
        return stocks

    except Exception as e:

        print(f"[ERROR] データ抽出失敗: {e}")

        return None


# =========================================
# JSON保存
# =========================================
def save_json(file_path, data):

    try:

        with open(file_path, "w", encoding="utf-8") as f:

            json.dump(
                data,
                f,
                ensure_ascii=False,
                indent=2
            )

        print(f"[OK] 保存: {file_path}")

    except Exception as e:

        print(f"[ERROR] JSON保存失敗: {e}")


# =========================================
# JSON読込
# =========================================
def load_json(file_path):

    try:

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:

            return json.load(f)

    except Exception as e:

        print(f"[ERROR] JSON読込失敗: {e}")

        return None


# =========================================
# 更新判定
# =========================================
def check_update():

    print("\n===== CHECK UPDATE =====")

    html = fetch_first_page()

    if not html:
        print("[実行] HTML取得失敗 → 続行")
        return True

    current_data = extract_stock_data(html)

    if not current_data:
        print("[実行] データ取得失敗 → 続行")
        return True

    # outputフォルダ作成
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 現在データ保存
    save_json(CURRENT_FILE, current_data)

    # 過去データ取得
    old_data = load_json(PREVIOUS_FILE)

    # 初回
    if old_data is None:
        print("[実行] 初回実行")
        return True

    # 比較（完全一致）
    if old_data == current_data:
        print("[STOP] 変更なし")
        return False

    print("[実行] 変更あり")
    return True


# =========================================
# スクレイパー本処理
# =========================================
def run_scraper():

    print("\n===== SCRAPER START =====")

    try:

        print("スクレイピング実行中...")

        # DB保存
        # CSV出力
        # Discord通知
        # etc

        print("[OK] 全処理正常終了")

        return True

    except Exception as e:

        print(f"[ERROR] scraper失敗: {e}")

        return False


# =========================================
# メイン
# =========================================
def main():

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    should_run = check_update()

    if not should_run:

        print("\n===== END =====")
        sys.exit(0)

    success = run_scraper()

    # 成功時のみ current → previous に更新
    if success:

        shutil.copy(CURRENT_FILE, PREVIOUS_FILE)

        print("[OK] previous.json 更新完了")

    else:

        print("[WARN] scraper失敗 → 更新なし")


# =========================================
# 実行
# =========================================
if __name__ == "__main__":

    main()
