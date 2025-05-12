import json
import requests
from flask import Flask, request, jsonify

# ————— Configuración directa de la API Key —————
RAPIDAPI_HOST = "sky-scrapper.p.rapidapi.com"
RAPIDAPI_KEY  = "a9e9833266msh6e1ebe861609386p12da89jsnb0b6f6f4636b"  # ← pon aquí tu key

app = Flask(__name__)

def get_flights(origin, destination, travel_date):
    """
    Llama a la API de RapidAPI (Air Scrapper) y devuelve una lista de vuelos.
    """
    url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchFlights"
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key":  RAPIDAPI_KEY
    }
    legs = json.dumps([{
        "origin":      origin,
        "destination": destination,
        "date":        travel_date
    }])
    params = {
        "legs":       legs,
        "currency":   "EUR",
        "locale":     "es-ES",
        "market":     "ES",
        "cabinClass": "economy"
    }

    resp = requests.get(url, headers=headers, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json().get("data", [])
    return [
        {
            "provider":    "sky-scrapper",
            "airline":     f.get("airline", "Unknown"),
            "origin":      origin,
            "destination": destination,
            "travel_date": travel_date,
            "price":       f.get("price", 0)
        }
        for f in data
    ]

@app.route('/flights', methods=['GET'])
def flights_endpoint():
    origin      = request.args.get('origin')
    destination = request.args.get('destination')
    travel_date = request.args.get('travel_date')

    if not all([origin, destination, travel_date]):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        flights = get_flights(origin, destination, travel_date)
    except requests.HTTPError as e:
        return jsonify({"error": f"API error: {e}"}), 502
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    return jsonify(flights), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)
