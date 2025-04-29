from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)

# Modelo de vuelo
class Flight:
    def __init__(self, provider, origin, destination, travel_date, price):
        self.provider = provider
        self.origin = origin
        self.destination = destination
        self.travel_date = travel_date
        self.price = price

    def to_dict(self):
        return {
            "provider": self.provider,
            "origin": self.origin,
            "destination": self.destination,
            "travel_date": self.travel_date.strftime("%Y-%m-%d"),  # Convertimos a string en formato YYYY-MM-DD
            "price": self.price
        }

# Ruta para buscar vuelos
@app.route("/flights", methods=["GET"])
def search_flights():
    # Obtenemos los parámetros de consulta
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    travel_date = request.args.get("travel_date")

    # Validamos que todos los parámetros existan
    if not origin or not destination or not travel_date:
        return jsonify({"error": "Missing required parameters"}), 400

    try:
        # Validamos la fecha
        travel_date = datetime.strptime(travel_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({"error": "Invalid date format. Use YYYY-MM-DD."}), 400

    # Lista de vuelos de ejemplo
    flights = [
        Flight(provider="ProviderA", origin=origin, destination=destination, travel_date=travel_date, price=120),
        Flight(provider="ProviderB", origin=origin, destination=destination, travel_date=travel_date, price=150)
    ]

    # Retornamos la lista de vuelos
    return jsonify([flight.to_dict() for flight in flights])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
