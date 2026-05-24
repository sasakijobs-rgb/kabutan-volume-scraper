import requests
from bs4 import BeautifulSoup
import csv
import os

URL = "https://s.kabutan.jp/warnings/trading_value_ranking/?market=all&page=1"

OUTPUT_DIR = "output"

TODAY_FILE = os.path.join(
    OUTPUT_DIR,
    "today_data20.csv"
)

LAST_FILE = os.path.join(
    OUTPUT_DIR,
    "last_data20.csv"
)


# =========================================
# CSV保存
# =========================================
def save_csv(path, rows):

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(
        path,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)

        writer.writerows(rows)


# =========================================
# CSV読み込み
# =========================================
def load_csv(path):

    if not os.path.exists(path):
        return None

    with open(
        path,
        "r",
        encoding="utf-8-sig"
    ) as f:

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

    r = requests.get(
        URL,
        headers=headers,
        timeout=30
    )

    if r.status_code != 200:

        print(
            f"[ERROR] status={r.status_code}"
        )

        return []

    soup = BeautifulSoup(
        r.text,
        "html.parser"
    )

    rows = soup.select("table tbody tr")

    data = []

    for row in rows:

        text = row.get_text(
            " ",
            strip=True
        )

        if not text:
            continue

        text = text.replace(
            "かぶたん プレミアム",
            ""
        )

        parts = text.split()

        if len(parts) < 10:
            continue

        data.append(parts[:10])

    return data


# =========================================
# 更新判定
# =========================================
def is_updated():

    current = fetch_page()

    if not current:

        print("[ERROR] データ取得失敗")

        return False

    save_csv(TODAY_FILE, current)

    old = load_csv(LAST_FILE)

    # 初回
    if old is None:

        print(
            "[INFO] 初回実行 "
            "(last_data20.csvなし)"
        )

        return True

    if old == current:

        print("[STOP] 変更なし")

        return False

    print("[RUN] 更新あり")

    return True


# =========================================
# last更新
# =========================================
def update_last():

    current = load_csv(TODAY_FILE)

    if current is not None:

        save_csv(LAST_FILE, current)

        print("[INFO] last_data20.csv更新")
