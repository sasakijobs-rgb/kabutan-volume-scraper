def check_update():

    print("\n===== HASH CHECK =====")

    html = fetch_first_page()

    if not html:
        print("[実行] 取得失敗（続行）")
        return True, None

    table_html = extract_table_html(html)

    new_hash = make_hash(table_html)
    old_hash = load_old_hash()

    print(f"[NEW HASH] {new_hash}")
    print(f"[OLD HASH] {old_hash}")

    # 初回
    if old_hash is None:
        print("[実行] ハッシュファイルなし")
        return True, new_hash

    # 変更なし
    if old_hash == new_hash:
        print("[STOP] データ変更なし → scraper停止")
        return False, None

    # 変更あり
    print("[実行] データ更新あり")
    return True, new_hash


def main():
    check_update()


if __name__ == "__main__":
    main()
