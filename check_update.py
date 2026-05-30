def check_update():

    print("===== CHECK START =====")

    # ① 今回データ取得
    today = fetch_page()

    # ② today保存
    save_csv(TODAY_FILE, today)
    print(f"[INFO] today saved: {len(today)} rows")

    # ③ last読み込み
    last = load_csv(LAST_FILE)

    # 初回実行
    if last is None:
        print("[INFO] 初回実行（lastなし）")
        return True

    # =========================
    # ④ 完全一致チェック
    # =========================
    if last == today:
        print("[OK] 変更なし（完全一致）")
        return False

    # =========================
    # ⑤ 差分表示（display）
    # =========================
    print("[DIFF] 変更あり\n")

    last_set = set(tuple(row) for row in last)
    today_set = set(tuple(row) for row in today)

    added = today_set - last_set
    removed = last_set - today_set

    if added:
        print("=== 追加データ（NEW） ===")
        for row in added:
            print(list(row))

    if removed:
        print("\n=== 削除データ（REMOVED） ===")
        for row in removed:
            print(list(row))

    print("\n[RUN] 更新あり")
    return True
