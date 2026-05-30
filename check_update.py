import requests
from bs4 import BeautifulSoup
import csv
import os
import time

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

OUTPUT_DIR = "output"

TODAY_FILE = os.path.join(OUTPUT_DIR, "today_data20.csv")
LAST_FILE = os.path.join(OUTPUT_DIR, "last_data20.csv")


# =========================================
# CSV保存
# =========================================
def save_csv(path, rows):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print("[DEBUG] save:", os.path.abspath(path))

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print("[DEBUG] saved rows:", len(rows))
    print("[DEBUG] mtime:", time.ctime(os.path.getmtime(path)))


# =========================================
# CSV読み込み
# =========================================
def load_csv(path):

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


# =========================================
# 1ページ取得
# =========================================
def fetch_page():

    headers = {
        "User-Agent": (
            "Mozilla/5.0 "
            "(Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 "
            "(KHTML, like Gecko) "
            "Chrome/125.0 Safari/537.36"
        ),
        "Accept-Language": "ja,en-US;q=0.9",
        "Referer": "https://s.kabutan.jp/"
    }

    r = requests.get(URL, headers=headers, timeout=30)

    print("[DEBUG] status:", r.status_code)
    print("[DEBUG] html size:", len(r.text))

    if r.status_code != 200:
        print(f"[ERROR] status={r.status_code}")
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    rows = soup.select("table tbody tr")

    print("[DEBUG] rows:", len(rows))

    data = []

    for row in rows:

        text = row.get_text(" ", strip=True)

        if not text:
            continue

        text = text.replace("かぶたん プレミアム", "")

        parts = text.split()

        if len(parts) < 10:
            continue

        data.append(parts[:10])

    print("[DEBUG] parsed data:", len(data))

    return data


# =========================================
# 更新判定
# =========================================
def is_updated():

    current = fetch_page()

    # TODAY保存
    save_csv(TODAY_FILE, current)

    if not current:
        print("[ERROR] データ取得失敗（TODAYは更新済み）")
        return False

    old = load_csv(LAST_FILE)

    if old is None:
        print("[INFO] 初回実行（lastなし）")
        return True

    if old == current:
        print("[DEBUG] old rows:", len(old))
        print("[DEBUG] current rows:", len(current))
        print("[STOP] 変更なし")
        return False

    print("[RUN] 更新あり")
    return True


# =========================================
# LAST更新
# =========================================
def update_last():

    current = load_csv(TODAY_FILE)

    if current is not None:
        save_csv(LAST_FILE, current)
        print("[INFO] last_data20.csv更新")


# =========================================
# MAIN
# =========================================
if __name__ == "__main__":

    print("===== scraper.py START =====")

    print("cwd =", os.getcwd())
    print("TODAY =", os.path.abspath(TODAY_FILE))
    print("LAST  =", os.path.abspath(LAST_FILE))

    if not is_updated():
        print("[ABORT] scraper.py 終了")
        exit()

    update_last()

    print("===== scraper.py END =====")
