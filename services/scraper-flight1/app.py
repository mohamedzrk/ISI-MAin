from flask import Flask, request, jsonify
import requests
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

@app.route("/flights")
def get_flights():
    origin = request.args.get("origin")
    destination = request.args.get("destination")
    travel_date = request.args.get("travel_date")

    if not origin or not destination or not travel_date:
        return jsonify({"error": "Missing parameters"}), 400

    url = "https://api.skypicker.com/flights"
    params = {
        "fly_from": origin,
        "fly_to": destination,
        "date_from": travel_date.replace("-", "/"),
        "date_to": travel_date.replace("-", "/"),
        "partner": "picky",
        "limit": 10,
        "curr": "EUR"
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.kiwi.com/",
        "Origin": "https://www.kiwi.com"
    }

    try:
        logging.info(f"Requesting Skypicker: {url} params={params}")
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return jsonify(data.get("data", []))
    except requests.RequestException as e:
        logging.error(f"Error calling Skypicker API: {e}")
        return jsonify({"error": "External API request failed"}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4002)
