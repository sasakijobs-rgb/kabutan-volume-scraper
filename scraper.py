import os
from datetime import datetime

# フォルダ作成
os.makedirs("output", exist_ok=True)

# ファイル作成
filename = f"output/test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"

with open(filename, "w", encoding="utf-8") as f:
    f.write("test,data\n")
    f.write("ok,1\n")

print("✅ test scraper success")