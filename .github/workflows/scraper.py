name: DataScraper

on:
  schedule:
    - cron: "0 7 * * *"

  workflow_dispatch:
    inputs:
      mode:
        description: "実行モード"
        required: false
        default: "normal"
        type: choice
        options:
          - normal
          - cleanup
          - nikkei_vi
          - nikkei_avg
          - data2csv
          - stock_reports
          - supabase

permissions:
  contents: write

jobs:
  scrape:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Install Chrome
        run: |
          wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
          sudo apt-get update
          sudo apt-get install -y ./google-chrome-stable_current_amd64.deb

      - name: Create output
        run: mkdir -p output

      - name: Run scraper
        env:
          SUPABASE_URL: ${{ secrets.SUPABASE_URL }}
          SUPABASE_KEY: ${{ secrets.SUPABASE_KEY }}
        run: |
          MODE="${{ github.event.inputs.mode }}"
          if [ -z "$MODE" ]; then
            MODE="normal"
          fi

          echo "[MODE] $MODE"
          python scraper.py "$MODE"

      - name: Commit CSV
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "github-actions[bot]@users.noreply.github.com"

          git add output/*.csv || true

          git diff --staged --quiet || git commit -m "Update CSV"

          git push

      - name: Upload artifacts
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: output
          path: output/
