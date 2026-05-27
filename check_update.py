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

        # ⚠ 現実的に厳しすぎるので緩めてもOK
        if len(parts) < 10:
            continue

        data.append(parts[:10])

    print("[DEBUG] parsed data:", len(data))

    return data


# =========================================
# 更新判定（あなた仕様）
# =========================================
def is_updated():

    # ① 取得
    current = fetch_page()

    # ② ★必ずTODAY保存（成功/失敗問わず記録）
    save_csv(TODAY_FILE, current)

    # ③ 取得失敗チェック（記録は済んでいる）
    if not current:
        print("[ERROR] データ取得失敗（TODAYは更新済み）")
        return False

    # ④ LAST読み込み
    old = load_csv(LAST_FILE)

    # ⑤ 初回
    if old is None:
        print("[INFO] 初回実行（lastなし）")
        return True

    # ⑥ 比較
    if old == current:
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
