from flask import Flask, request, jsonify
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/flights")
def get_flights():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    travel_date = request.args.get("travel_date")  # formato YYYY-MM-DD

    if not all([origin, destination, travel_date]):
        return jsonify({"error": "Missing parameters"}), 400

    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            # Ir a la página de búsqueda de Kiwi
            page.goto("https://www.kiwi.com/es/")

            # Rellenar formulario
            page.fill('input[placeholder="¿Desde dónde?"]', origin)
            page.fill('input[placeholder="¿Hacia dónde?"]', destination)
            page.click('input[type="date"]')
            page.fill('input[type="date"]', travel_date)
            page.click('button:has-text("Buscar")')

            # Esperar a que carguen los resultados
            page.wait_for_selector('.ResultItem', timeout=20000)

            # Extraer algunos vuelos (limitar a 5)
            items = page.query_selector_all('.ResultItem')[:5]
            for item in items:
                price = item.query_selector('.Price_amount').inner_text().strip()
                depart = item.query_selector('.Segment-route .Segment-time').inner_text().split('–')[0].strip()
                arrive = item.query_selector('.Segment-route .Segment-time').inner_text().split('–')[1].strip()
                results.append({
                    "provider": "Playwright-Kiwi",
                    "origin": origin,
                    "destination": destination,
                    "travel_date": travel_date,
                    "price": float(price.replace('€','').replace(',','.')),
                    "depart_time": depart,
                    "arrival_time": arrive
                })

        except PlaywrightTimeout:
            logging.error("Timeout al cargar resultados")
        finally:
            browser.close()

    return jsonify(results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4002)
