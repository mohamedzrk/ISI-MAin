from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# URL de ejemplo para scrappear (Kayak)
# Construye la ruta en función de origen, destino y fecha: 
# https://www.kayak.com/flights/MAD-BCN/2025-05-20?sort=bestflight_a
BASE_URL = "https://www.kayak.com/flights"

@app.route('/flights', methods=['GET'])
def get_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    travel_date = request.args.get('travel_date')

    if not all([origin, destination, travel_date]):
        return jsonify({'error': 'Missing parameters'}), 400

    # Construir URL de Kayak
    flight_path = f"/{origin}-{destination}/{travel_date}"
    target_url = BASE_URL + flight_path + "?sort=bestflight_a"

    try:
        # Petición al sitio web (nota: Kayak carga contenido dinámicamente)
        resp = requests.get(target_url, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"Error fetching target page: {e}")
        return jsonify({'error': 'Failed to retrieve data'}), 502

    # Parsear el HTML (aunque normalmente Kayak usa JS)
    soup = BeautifulSoup(resp.text, 'lxml')
    flights = []

    # Ejemplo de selectores (ajusta según estructura real)
    for item in soup.select('.Base-Results-HorizonResult'):
        try:
            airline = item.select_one('.codeshares-airline-names').get_text(strip=True)
            price_text = item.select_one('.price-text').get_text(strip=True)
            price = float(price_text.replace('€', '').replace(',', '').replace('$', ''))
            origin_code = origin
            destination_code = destination
            depart_date = travel_date

            flights.append({
                'provider': airline,
                'origin': origin_code,
                'destination': destination_code,
                'travel_date': depart_date,
                'price': price
            })
        except Exception as e:
            logging.warning(f"Skipping item due to parse error: {e}")

    return jsonify(flights)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)
