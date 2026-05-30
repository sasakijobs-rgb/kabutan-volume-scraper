# =========================
# 制御py(ここから他pyを実行する)
# scraper.py
# →last_data20.csvとtoday_data20.csvを比べる
# (この２ファイルが同じなら全ての処理を停止する)
# (前回・今回の１ページ目の内容を出力して比較する）
# →cleanup.py
# (ファイルが150個以上は削除)
# →data2csv.py
# (株探のモバイル版からデータを取得）
# →merge.py
# (最初だけ見出しをセット＆２ファイル目以降はデータのみ)
# →nikkei_data_vi.csvを更新
# →last_data20.csvを更新
# (正常終了時のみlast～は更新されます)
# =========================
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
# データ取得
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
# 更新判定（scraper.pyから呼ばれる）
# =========================================
def check_update():

    print("===== CHECK START =====")

    # ① 毎回取得
    today = fetch_page()

    # ② todayは必ず保存（上書き）
    save_csv(TODAY_FILE, today)
    print(f"[INFO] today saved: {len(today)} rows")

    # ③ last読み込み
    last = load_csv(LAST_FILE)

    # 初回
    if last is None:
        print("[INFO] 初回実行（lastなし）")
        return True

    # ④ 比較（ファイル同士）
    if last == today:
        print("[STOP] 変更なし（last == today）")
        return False

    print("[RUN] 更新あり")
    return True


# =========================================
# last更新（YAMLから呼ぶ）
# =========================================
def update_last():

    today = load_csv(TODAY_FILE)

    if today is not None:
        save_csv(LAST_FILE, today)
        print("[INFO] last更新")
