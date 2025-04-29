import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

app = Flask(__name__)
CORS(app)

# URLs de microservicios desde variables de entorno o valores por defecto
CACHE_URL = os.environ.get('CACHE_URL', 'http://flight-cache:4004')
SEARCH_URL = os.environ.get('SEARCH_URL', 'http://search-flight:4000')
SCRAPER1_URL = os.environ.get('SCRAPER1_URL', 'http://scraper-flight1:4002')
SCRAPER2_URL = os.environ.get('SCRAPER2_URL', 'http://scraper-flight2:4003')

SERVICE_ENDPOINTS = [
    f"{SEARCH_URL}/flights",
    f"{SCRAPER1_URL}/flights",
    f"{SCRAPER2_URL}/flights"
]

@app.route('/flights', methods=['GET'])
def get_flights():
    ori = request.args.get('ori')
    dst = request.args.get('dst')
    date = request.args.get('date')
    
    try:
        # 1. Intentar cache
        cache_resp = requests.get(f"{CACHE_URL}/cache", params={"ori": ori, "dst": dst, "date": date})
        cache_data = cache_resp.json()
        if isinstance(cache_data, list) and cache_data:
            app.logger.info('Cache HIT')
            return jsonify(cache_data)
        app.logger.info('Cache MISS')
        
        # 2. Llamadas concurrentes a microservicios
        flights = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(requests.get, url, params={"ori": ori, "dst": dst, "date": date})
                       for url in SERVICE_ENDPOINTS]
            for future in as_completed(futures):
                try:
                    resp = future.result()
                    if resp.status_code == 200:
                        data = resp.json()
                        if isinstance(data, list):
                            flights.extend(data)
                except Exception as e:
                    app.logger.error(f"Error contacting service: {e}")

        # 3. Guardar en cache
        try:
            requests.post(f"{CACHE_URL}/cache", json={
                "ori": ori,
                "dst": dst,
                "date": date,
                "data": flights
            })
        except Exception as e:
            app.logger.warning(f"Failed to save cache: {e}")

        # 4. Ordenar por precio
        flights.sort(key=lambda x: x.get('price', float('inf')))
        return jsonify(flights)

    except Exception as err:
        app.logger.error(f"Error in /flights: {err}")
        return jsonify({"error": "Internal Gateway Error"}), 500

@app.route('/')
def index():
    return 'API Gateway está funcionando ✈️'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3001)
