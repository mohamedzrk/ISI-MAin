from flask import Flask, request, jsonify
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright
import logging
import traceback

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

BASE_URL = "https://www.kayak.com/flights"
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/113.0.0.0 Safari/537.36'
    )
}

def get_rendered_html(url: str) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS['User-Agent'])
        page.goto(url, wait_until='networkidle')
        html = page.content()
        browser.close()
        return html

@app.route('/flights', methods=['GET'])
def get_flights():
    origin      = request.args.get('origin')
    destination = request.args.get('destination')
    travel_date = request.args.get('travel_date')

    if not all([origin, destination, travel_date]):
        return jsonify({'error': 'Missing parameters'}), 400

    target_url = f"{BASE_URL}/{origin}-{destination}/{travel_date}?sort=bestflight_a"
    logging.info(f"Fetching (Playwright) {target_url}")

    try:
        html = get_rendered_html(target_url)
        # Imprime un fragmento para depurar
        print("=== RENDERED HTML START ===")
        print(html[:1000])
        print("=== RENDERED HTML END ===")
    except Exception:
        logging.error("Error rendering page:\n" + traceback.format_exc())
        return jsonify({'error': 'Render failed'}), 502

    soup = BeautifulSoup(html, 'lxml')
    flights = []

    for item in soup.select('.Base-Results-HorizonResult'):
        try:
            airline   = item.select_one('.codeshares-airline-names').get_text(strip=True)
            price_txt = item.select_one('.price-text').get_text(strip=True)
            price     = float(price_txt.replace('€', '').replace(',', '').replace('$', ''))
            flights.append({
                'airline':     airline,
                'origin':      origin,
                'destination': destination,
                'travel_date': travel_date,
                'price':       price
            })
        except Exception as e:
            logging.warning(f"Skipping item due to parse error: {e}")

    return jsonify(flights)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)
