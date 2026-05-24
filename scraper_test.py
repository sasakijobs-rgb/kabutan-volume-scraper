def check_update():

    print("\n===== HASH CHECK =====")

    html = fetch_first_page()

    if not html:
        print("[実行] 取得失敗（続行）")
        return True

    # =========================
    # table部分だけ抽出
    # =========================
    table_html = extract_table_html(html)

    new_hash = make_hash(table_html)
    old_hash = load_old_hash()

    print(f"[NEW HASH] {new_hash}")
    print(f"[OLD HASH] {old_hash}")

    # =========================
    # 判定ロジック
    # =========================

    if old_hash is None:
        print("[実行] ハッシュファイルなし")
        save_hash(new_hash)
        return True

    if old_hash == new_hash:
        print("[STOP] データ変更なし → scraper停止")
        return False

    print("[実行] データ更新あり")
    save_hash(new_hash)
    return True
