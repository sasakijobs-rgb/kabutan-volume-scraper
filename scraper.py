import os
import time
import random
import csv
import re
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

# ==========================================
# 設定
# ==========================================
BASE_URL = (
    "https://s.kabutan.jp/warnings/"
    "trading_value_ranking/?market=all&page={}"
)

MAX_PAGES = 300

today = datetime.now().strftime("%Y%m%d")

os.makedirs("output", exist_ok=True)

merged_file = "output/trading_value_ranking_merged.csv"
daily_file = f"output/trading_value_ranking_{today}.csv"

# ==========================================
# CSVヘッダー
# ==========================================
header = [
    "日付",
    "順位",
    "コード",
    "銘柄名",
    "市場",
    "株価(百万円)",
    "前日比(値)",
    "前日比(率)",
    "売買代金",
    "PER",
    "PBR",
    "利回り"
]

# ==========================================
# merged 初回作成
# ==========================================
if not os.path.exists(merged_file):

    with open(
        merged_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as f:

        writer = csv.writer(f)
        writer.writerow(header)

# ==========================================
# 古い日次CSV削除（150件保持）
# ==========================================
def cleanup_old_daily_files():

    folder = "output"

    prefix = "trading_value_ranking_"
    suffix = ".csv"

    files = []

    for f in os.listdir(folder):

        if not f.startswith(prefix):
            continue

        if not f.endswith(suffix):
            continue

        # merged除外
        if "merged" in f:
            continue

        date_str = (
            f.replace(prefix, "")
             .replace(suffix, "")
        )

        if not date_str.isdigit():
            continue

        files.append((date_str, f))

    # 古い順
    files.sort(key=lambda x: x[0])

    MAX_FILES = 150

    if len(files) > MAX_FILES:

        delete_targets = files[:len(files) - MAX_FILES]

        for _, filename in delete_targets:

            path = os.path.join(folder, filename)

            try:
                os.remove(path)
                print("🗑 削除:", filename)

            except Exception as e:
                print("⚠ 削除失敗:", filename, e)

# ==========================================
# Chrome
# ==========================================
options = Options()

options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--disable-gpu")

options.add_argument("--window-size=1400,2200")

options.add_argument(
    "--user-agent=Mozilla/5.0 "
    "(Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 "
    "(KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

driver = webdriver.Chrome(options=options)

# ==========================================
# メイン
# ==========================================
try:

    print("===== START =====")

    cleanup_old_daily_files()

    # ==========================================
    # CSV準備
    # ==========================================
    with open(
        daily_file,
        "w",
        newline="",
        encoding="utf-8-sig"
    ) as df, open(
        merged_file,
        "a",
        newline="",
        encoding="utf-8-sig"
    ) as mf:

        daily_writer = csv.writer(df)
        merged_writer = csv.writer(mf)

        # dailyのみヘッダー
        daily_writer.writerow(header)

        rank = 1
        empty_count = 0

        # ==========================================
        # ページループ
        # ==========================================
        for page in range(1, MAX_PAGES + 1):

            url = BASE_URL.format(page)

            print("\n===================================")
            print("PAGE:", page)
            print(url)

            driver.get(url)

            time.sleep(random.uniform(2, 4))

            rows = driver.find_elements(
                By.CSS_SELECTOR,
                "tbody tr"
            )

            print("rows:", len(rows))

            # ==========================================
            # 空ページ判定
            # ==========================================
            if len(rows) == 0:

                empty_count += 1

                print(
                    f"⚠ empty page "
                    f"({empty_count})"
                )

                if empty_count >= 3:
                    print("⚠ 3連続空ページ → 終了")
                    break

                continue

            empty_count = 0

            page_valid_count = 0

            # ==========================================
            # 行解析
            # ==========================================
            for row in rows:

                try:

                    txt = row.text.strip()

                    # 空行除外
                    if not txt:
                        continue

                    lines = txt.split("\n")

                    # ======================================
                    # コード行探索
                    # ======================================
                    code_index = -1

                    for i, line in enumerate(lines):

                        code = line.strip().upper()

                        # 英数字4〜5文字
                        if re.fullmatch(
                            r"[A-Z0-9]{4,5}",
                            code
                        ):
                            code_index = i
                            break

                    # コード無し
                    if code_index == -1:
                        continue

                    # ======================================
                    # 必須行数
                    # ======================================
                    if len(lines) < code_index + 4:
                        continue

                    # ======================================
                    # データ取得
                    # ======================================
                    name = lines[code_index - 1].strip()

                    code = (
                        lines[code_index]
                        .strip()
                        .upper()
                    )

                    market = lines[code_index + 1].strip()

                    price_prev = (
                        lines[code_index + 2]
                        .strip()
                    )

                    remain = (
                        lines[code_index + 3]
                        .strip()
                    )

                    print("\n-------------------")
                    print("name :", name)
                    print("code :", code)
                    print("market :", market)
                    print("price_prev :", price_prev)
                    print("remain :", remain)

                    # ======================================
                    # 株価 / 前日比
                    # ======================================
                    m = re.match(
                        r"(.+?)\s+([+-].+)",
                        price_prev
                    )

                    if m:
                        price = m.group(1)
                        prev_value = m.group(2)
                    else:
                        price = price_prev
                        prev_value = ""

                    parts = remain.split()

                    prev_rate = (
                        parts[0]
                        if len(parts) > 0
                        else ""
                    )

                    trading_value = (
                        parts[1]
                        if len(parts) > 1
                        else ""
                    )

                    per = (
                        parts[2]
                        if len(parts) > 2
                        else ""
                    )

                    pbr = (
                        parts[3]
                        if len(parts) > 3
                        else ""
                    )

                    yield_value = (
                        parts[4]
                        if len(parts) > 4
                        else ""
                    )

                    # ======================================
                    # カンマ除去
                    # ======================================
                    price = (
                        price.replace(",", "")
                    )

                    prev_value = (
                        prev_value.replace(",", "")
                    )

                    trading_value = (
                        trading_value.replace(",", "")
                    )

                    # ======================================
                    # CSVデータ
                    # ======================================
                    row_data = [
                        today,
                        rank,
                        code,
                        name,
                        market,
                        price,
                        prev_value,
                        prev_rate,
                        trading_value,
                        per,
                        pbr,
                        yield_value
                    ]

                    daily_writer.writerow(row_data)
                    merged_writer.writerow(row_data)

                    page_valid_count += 1

                    print(
                        "✔",
                        rank,
                        code,
                        name
                    )

                    rank += 1

                except Exception as e:

                    print("⚠ row error:", e)

                    try:
                        print(
                            row.get_attribute(
                                "innerHTML"
                            )
                        )
                    except:
                        pass

                    continue

            print(
                "valid rows:",
                page_valid_count
            )

    print("\n===== 完了 =====")

    print("daily :", daily_file)
    print("merged:", merged_file)

finally:

    driver.quit()

    print("===== END =====")
