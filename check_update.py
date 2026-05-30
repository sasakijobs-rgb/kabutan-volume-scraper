import requests
from bs4 import BeautifulSoup
import csv
import os

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

OUTPUT_DIR = "output"

TODAY_FILE = os.path.join(OUTPUT_DIR, "today_data20.csv")
LAST_FILE = os.path.join(OUTPUT_DIR, "last_data20.csv")


# =========================================
# CSV保存
# =========================================
def save_csv(path, rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


# =========================================
# CSV読み込み
# =========================================
def load_csv(path):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


# =========================================
# 取得
# =========================================
def fetch_page():

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "ja,en-US;q=0.9"
    }

    r = requests.get(URL, headers=headers, timeout=30)

    if r.status_code != 200:
        print("[ERROR] status:", r.status_code)
        return []

    soup = BeautifulSoup(r.text, "html.parser")
    rows = soup.select("table tbody tr")

    data = []

    for row in rows:
        text = row.get_text(" ", strip=True)
        text = text.replace("かぶたん プレミアム", "")
        parts = text.split()

        if len(parts) < 10:
            continue

        data.append(parts[:10])

    return data


# =========================================
# 比較（ファイル同士）
# =========================================
def is_updated():

    # ① 今回取得
    current = fetch_page()

    # ② today保存
    save_csv(TODAY_FILE, current)

    # ③ last読み込み
    old = load_csv(LAST_FILE)

    # 初回
    if old is None:
        print("[INFO] 初回実行")
        return True

    # ④ ★ここが本題（ファイル比較）
    if old == current:
        print("[STOP] 変更なし（last == today）")
        return False

    print("[RUN] 更新あり")
    return True


# =========================================
# last更新（成功時のみ）
# =========================================
def update_last():
    today = load_csv(TODAY_FILE)

    if today is not None:
        save_csv(LAST_FILE, today)
        print("[INFO] last更新")


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    print("===== START =====")

    if not is_updated():
        print("[ABORT]")
        exit()

    update_last()

    print("===== END =====")
