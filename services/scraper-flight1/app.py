# Importa módulos necesarios
import os                      # Para acceder a variables de entorno
import requests                # Para hacer peticiones HTTP
from flask import Flask, request, jsonify  # Framework web y utilidades

# Crea una instancia de Flask (el servidor web)
app = Flask(__name__)

# === Configuración ===

# Obtiene la clave de la API de RapidAPI desde una variable de entorno
# Si no está definida, usa una clave por defecto (inseguro para producción)
RAPIDAPI_KEY = os.getenv(
    "RAPIDAPI_KEY",
    "a9e9833266msh6e1ebe861609386p12da89jsnb0b6f6f4636b"
)

# Obtiene el host de RapidAPI desde una variable de entorno (o usa valor por defecto)
HOST = os.getenv("RAPIDAPI_HOST", "google-flights4.p.rapidapi.com")

# URL base del endpoint de búsqueda de vuelos de ida
BASE_URL = f"https://{HOST}/flights/search-one-way"

def buscar_precio_ida(departure_id: str, arrival_id: str, departure_date: str):
    """
    Llama al endpoint /flights/search-one-way de RapidAPI y devuelve la respuesta en JSON.
    Parámetros:
        departure_id: código IATA del aeropuerto de salida (ej. JFK)
        arrival_id:   código IATA del aeropuerto de llegada (ej. LAX)
        departure_date: fecha del vuelo en formato YYYY-MM-DD
    """
    # Encabezados necesarios para autenticar con RapidAPI
    headers = {
        "x-rapidapi-key": RAPIDAPI_KEY,
        "x-rapidapi-host": HOST
    }

    # Parámetros de la consulta
    params = {
        "departureId":   departure_id,
        "arrivalId":     arrival_id,
        "departureDate": departure_date
    }

    # Realiza la petición a la API
    resp = requests.get(BASE_URL, headers=headers, params=params, timeout=10)

    # Si hay un error HTTP (status 4xx o 5xx), lanza una excepción
    resp.raise_for_status()

    # Devuelve el JSON crudo
    return resp.json()

# === Endpoints de la API ===

@app.route('/', methods=['GET'])
def health_check():
    # Ruta raíz para verificar que el servicio está vivo
    return jsonify({"status": "ok"}), 200

@app.route('/flights', methods=['GET'])
def flights_endpoint():
    # Extrae los parámetros de la URL: origen, destino y fecha
    origin      = request.args.get('origin')
    destination = request.args.get('destination')
    travel_date = request.args.get('travel_date')  # Formato: YYYY-MM-DD

    # Verifica que todos los parámetros estén presentes
    if not all([origin, destination, travel_date]):
        return jsonify({"error": "Missing parameters"}), 400

    # Intenta llamar a la API de RapidAPI para obtener vuelos
    try:
        raw = buscar_precio_ida(origin, destination, travel_date)
    except requests.HTTPError as e:
        # Error HTTP de la API externa
        return jsonify({
            "error":   f"Upstream API error: {e}",
            "details": e.response.text
        }), 502
    except Exception as e:
        # Otro tipo de error inesperado
        return jsonify({"error": f"Unexpected error: {e}"}), 500

    # Intenta acceder al array de vuelos: data → otherFlights
    data = raw.get("data", {})
    flights = data.get("otherFlights", [])

    # Si no se pudo extraer la lista de vuelos, devuelve error
    if not isinstance(flights, list):
        return jsonify({
            "error":    "Could not extract flights array from upstream",
            "upstream": raw
        }), 502

    # === Normalización de datos ===

    # Lista para almacenar los vuelos transformados
    normalized = []
    for f in flights:
        price = f.get("price")  # Precio del vuelo
        carrier = None

        # Intenta extraer el nombre de la aerolínea
        if isinstance(f.get("airline"), list) and f["airline"]:
            carrier = f["airline"][0].get("airlineName")

        # Si no se encontró, usa airlineCode o "Unknown"
        carrier = carrier or f.get("airlineCode") or "Unknown"

        # Crea un objeto vuelo estandarizado
        normalized.append({
            "provider":    "google-flights",
            "airline":     carrier,
            "origin":      origin,
            "destination": destination,
            "travel_date": travel_date,
            "price":       price
        })

    # Devuelve la lista de vuelos normalizados como JSON
    return jsonify(normalized), 200

# Lanza el servidor si se ejecuta este archivo directamente
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)
