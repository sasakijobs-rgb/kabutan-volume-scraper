import requests
from bs4 import BeautifulSoup
import json
import os

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all"

OUTPUT_DIR = "output"
TODAY_FILE = os.path.join(OUTPUT_DIR, "today.json")
LAST_FILE = os.path.join(OUTPUT_DIR, "last.json")


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

    # 必ず保存
    save_json(TODAY_FILE, current)

    old = load_json(LAST_FILE)

    # 初回
    if old is None:
        print("[INFO] 初回実行")
        return True

    # 比較
    if old == current:
        print("[STOP] 変更なし")
        return False

    print("[RUN] 更新あり")
    return True


# =========================================
# main
# =========================================
def main():

    if not is_updated():
        return

    print("スクレイピング実行")


    # ここに本処理を書く
    # DB保存・通知など

    # 成功したら last更新
    with open(TODAY_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    save_json(LAST_FILE, data)

    print("[DONE]")


if __name__ == "__main__":
    main()
