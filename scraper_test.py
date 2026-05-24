import json

def extract_stock_data(html):

    soup = BeautifulSoup(html, "html.parser")

    rows = soup.select("table.stock_table.st_market tbody tr")

    result = []

    for row in rows:

        cols = row.find_all(["td", "th"])

        item = {
            "code": cols[0].get_text(strip=True),
            "name": cols[1].get_text(strip=True),
            "price": cols[5].get_text(strip=True),
            "change_percent": cols[8].get_text(strip=True),
        }

        result.append(item)

    return json.dumps(result, ensure_ascii=False, sort_keys=True)
