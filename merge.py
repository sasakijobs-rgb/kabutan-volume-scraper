import re
import os

filename = os.path.basename(file_path)

pattern = r"^trading_value_ranking_\d{8}\.csv$"

if re.match(pattern, filename):
    print("OK: 正しい形式のファイルです →", filename)
else:
    print("NG: 想定外のファイルです →", filename)
