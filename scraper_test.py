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
# 1ページ目取得
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
        text = row.get_text(" ", strip=True)
        text = text.replace("かぶたん プレミアム", "")
        parts = text.split()

        if len(parts) < 10:
            continue

        data.append(parts[:10])

    return data


# =========================
# 更新チェック
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
        print("[STOP] 変更なし（完全一致）")
        return False

    print("[RUN] 更新あり")
    return True


# =========================
# last更新
# =========================
def update_last():

    today = load_csv(TODAY_FILE)

    if today is not None:
        save_csv(LAST_FILE, today)
        print("[INFO] last更新")


# =========================
# main
# =========================
if __name__ == "__main__":

    # ① 更新チェック
    if not check_update():
        print("[EXIT] 変更なし → 処理終了")
        exit(1)

    # ② ここに本処理を追加する想定
    print("[RUN] 本処理実行（ここにscraperやSupabase処理）")

    # ③ 成功時のみlast更新
    update_last()

    print("[DONE] 完了")
