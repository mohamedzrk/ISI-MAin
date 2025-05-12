import os
import requests
import json

RAPIDAPI_HOST = "sky-scrapper.p.rapidapi.com"
RAPIDAPI_KEY  = os.getenv("RAPIDAPI_KEY")  # Define esta var. en Docker

def get_flights(origin, destination, travel_date):
    url = f"https://{RAPIDAPI_HOST}/api/v1/flights/searchFlights"
    headers = {
        "X-RapidAPI-Host": RAPIDAPI_HOST,
        "X-RapidAPI-Key":  RAPIDAPI_KEY
    }
    # Convertimos el legs a una cadena JSON para pasarlo en la query
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
    # Devolver solo los campos más relevantes
    return [
        {
            "provider":    "sky-scrapper",
            "airline":     flight.get("airline", "Unknown"),
            "origin":      origin,
            "destination": destination,
            "travel_date": travel_date,
            "price":       flight.get("price", 0)
        }
        for flight in data
    ]

# Ejemplo de uso
if __name__ == "__main__":
    vuelos = get_flights("BCN", "MAD", "2025-06-01")
    print(json.dumps(vuelos, indent=2, ensure_ascii=False))
