import requests
from bs4 import BeautifulSoup
import hashlib
import os
import shutil
import sys

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all"

TODAY_HASH_FILE = "today_hash.txt"
LAST_HASH_FILE = "last_hash.txt"


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

    except requests.RequestException as e:

        print(f"[ERROR] HTML取得失敗: {e}")

        return None


# =========================================
# gray-sticky-table 抽出
# =========================================
def extract_table_html(html):

    if not html:
        return ""

    try:

        soup = BeautifulSoup(html, "html.parser")

        table = soup.find(
            "table",
            class_="gray-sticky-table"
        )

        if table is None:

            print("[ERROR] gray-sticky-table が見つかりません")

            return ""

        print("[OK] テーブル抽出成功")

        return str(table).strip()

    except Exception as e:

        print(f"[ERROR] テーブル抽出失敗: {e}")

        return ""


# =========================================
# SHA256生成
# =========================================
def make_hash(text):

    if text is None:
        text = ""

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


# =========================================
# ハッシュ読込
# =========================================
def load_hash(file_path):

    try:

        if not os.path.exists(file_path):
            return None

        with open(file_path, "r", encoding="utf-8") as f:

            return f.read().strip()

    except Exception as e:

        print(f"[ERROR] ハッシュ読込失敗: {e}")

        return None


# =========================================
# ハッシュ保存
# =========================================
def save_hash(file_path, hash_value):

    try:

        with open(file_path, "w", encoding="utf-8") as f:

            f.write(hash_value)

        print(f"[OK] 保存完了: {file_path}")

    except Exception as e:

        print(f"[ERROR] ハッシュ保存失敗: {e}")


# =========================================
# today → last
# 正常終了時のみ呼ぶ
# =========================================
def finalize_hash():

    try:

        if not os.path.exists(TODAY_HASH_FILE):

            print("[WARN] today_hash.txt が存在しません")

            return

        shutil.copy(
            TODAY_HASH_FILE,
            LAST_HASH_FILE
        )

        print("[OK] last_hash.txt 更新完了")

    except Exception as e:

        print(f"[ERROR] last_hash 更新失敗: {e}")


# =========================================
# 更新チェック
# =========================================
def check_update():

    print("\n===== HASH CHECK =====")

    old_hash = load_hash(LAST_HASH_FILE)

    # HTML取得
    html = fetch_first_page()

    if not html:

        print("[実行] HTML取得失敗 → 続行")

        return True

    # テーブル抽出
    table_html = extract_table_html(html)

    if not table_html:

        print("[実行] テーブル取得失敗 → 続行")

        return True

    # 新hash生成
    new_hash = make_hash(table_html)

    print(f"[NEW HASH] {new_hash}")
    print(f"[OLD HASH] {old_hash}")

    # 今回hash保存
    save_hash(TODAY_HASH_FILE, new_hash)

    # 初回
    if old_hash is None:

        print("[実行] 初回実行")

        return True

    # 更新なし
    if old_hash == new_hash:

        print("[STOP] 更新なし → scraper停止")

        return False

    # 更新あり
    print("[実行] 更新あり → scraper実行")

    return True


# =========================================
# 本処理
# =========================================
def run_scraper():

    print("\n===== SCRAPER START =====")

    try:

        # =====================================
        # ここに本スクレイピング処理を書く
        # =====================================

        print("スクレイピング実行中...")

        # 例:
        # save_db()
        # send_discord()
        # export_csv()

        print("[OK] 全処理正常終了")

        return True

    except Exception as e:

        print(f"[ERROR] scraper失敗: {e}")

        return False


# =========================================
# メイン
# =========================================
def main():

    should_run = check_update()

    if not should_run:

        print("\n===== END =====")

        sys.exit(0)

    # scraper実行
    success = run_scraper()

    # 正常終了時のみ last_hash 更新
    if success:

        finalize_hash()

    else:

        print("[WARN] scraper失敗のため last_hash 更新しません")


# =========================================
# 実行
# =========================================
if __name__ == "__main__":

    main()
