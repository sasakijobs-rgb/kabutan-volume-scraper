name: kabutan-volume-scraper

on:
schedule:
# 毎日 日本時間 17:00 実行（UTC 08:00）
- cron: '0 8 * * *'
workflow_dispatch:

jobs:
run-scraper:
runs-on: ubuntu-latest

```
steps:

  - name: Checkout repository
    uses: actions/checkout@v5

  - name: Set up Python
    uses: actions/setup-python@v5
    with:
      python-version: "3.11"

  - name: Install libraries
    run: |
      python -m pip install --upgrade pip
      pip install requests beautifulsoup4 pandas

  - name: Run scraper
    run: |
      python scraper.py

  - name: Commit CSV files
    run: |
      git config --local user.email "action@github.com"
      git config --local user.name "github-actions"
      git add output/*.csv
      git commit -m "Update volume ranking data" || echo "No changes to commit"
      git push
```
