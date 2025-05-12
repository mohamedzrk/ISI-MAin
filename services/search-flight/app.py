import requests
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

SCRAPER_URLS = [
    "http://scraper-flight1:4002/flights",
    "http://scraper-flight2:4003/flights"
]

FLIGHT_CACHE_URL = "http://flight-cache:4004/cache"
HEADERS = {
    'User-Agent': (
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
        'AppleWebKit/537.36 (KHTML, like Gecko) '
        'Chrome/113.0.0.0 Safari/537.36'
    )
}

@app.route('/flights', methods=['GET'])
def search_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    travel_date = request.args.get('travel_date')

    if not all([origin, destination, travel_date]):
        return jsonify({'error': 'Missing parameters'}), 400

    try:
        datetime.strptime(travel_date, '%Y-%m-%d')
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    results = []
    for url in SCRAPER_URLS:
        try:
            resp = requests.get(
                url,
                params={"origin": origin, "destination": destination, "travel_date": travel_date},
                headers=HEADERS,
                timeout=10
            )
            resp.raise_for_status()
            flights = resp.json()
            for f in flights:
                f["airline"] = f.pop("provider", f.get("airline", "Unknown"))
            results.extend(flights)
        except Exception as e:
            app.logger.warning(f"⚠️ Error fetching from {url}: {e}")

    try:
        requests.post(
            FLIGHT_CACHE_URL,
            json=results,
            headers=HEADERS,
            timeout=5
        ).raise_for_status()
        app.logger.info("✅ Guardado en caché.")
    except Exception as e:
        app.logger.warning(f"❌ Error al guardar en caché: {e}")

    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
