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
from check_update import check_update, update_last

# =========================================
# メイン処理
# =========================================
if __name__ == "__main__":

    print("===== scraper.py START =====")

    # ① 更新チェック（ここで取得＋比較まで実行される）
    if not check_update():
        print("[STOP] 変更なし")
        print("[ABORT] scraper.py 終了")
        exit()

    # ② 変更ありの場合のみ last 更新
    update_last()

    print("[END] 処理完了")
