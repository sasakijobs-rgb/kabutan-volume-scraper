import requests
from bs4 import BeautifulSoup
import csv
import os

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

OUTPUT_DIR = "output"
TODAY_FILE = os.path.join(OUTPUT_DIR, "today_data20.csv")
LAST_FILE = os.path.join(OUTPUT_DIR, "last_data20.csv")


# =========================
# CSV保存
# =========================
def save_csv(path, rows):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerows(rows)


# =========================
# CSV読み込み
# =========================
def load_csv(path):
    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8-sig") as f:
        return list(csv.reader(f))


# =========================
# データ取得（安定版）
# =========================
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
        cells = [td.get_text(strip=True) for td in row.find_all("td")]

        # 列数が足りない行は除外
        if len(cells) < 10:
            continue

        data.append(cells[:10])

    return data


# =========================
# 更新チェック（これだけ使う）
# =========================
def check_update():
    print("===== CHECK START =====")

    today = fetch_page()
    save_csv(TODAY_FILE, today)
    print(f"[INFO] today saved: {len(today)} rows")

    last = load_csv(LAST_FILE)

    if last is None:
        print("[INFO] 初回実行（lastなし）")
        return True

    if last == today:
        print("[STOP] 変更なし")
        return False

    print("[RUN] 更新あり")
    return True


# =========================
# 実行
# =========================
if __name__ == "__main__":
    check_update()
