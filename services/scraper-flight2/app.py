from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from dateutil import parser
import re

app = Flask(__name__)

BASE_URL = (
    "https://azair.eu/azfin.php"
    "?searchtype=flexi&adults=1&children=0&infants=0"
    "&bags=1&currency=EUR&max_fly_days=0&max_transfers=0"
)
# Azair aplica filtros por defecto low-cost → históricamente muy fiable.

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/113.0.0.0 Safari/537.36"
    )
}

def build_url(origin: str, dest: str, date: str) -> str:
    """
    date: YYYY-MM-DD → Azair necesita DD.MM.YYYY
    """
    ddmmyyyy = datetime.strptime(date, "%Y-%m-%d").strftime("%d.%m.%Y")
    return f"{BASE_URL}&origin={origin}&destination={dest}&out={ddmmyyyy}"

def parse_flights(html: str, origin: str, dest: str, date: str):
    soup = BeautifulSoup(html, "html.parser")
    rows = soup.select("tr[id^='tr_']")  # cada resultado tiene id="tr_..."
    flights = []

    for row in rows[:10]:  # hasta 10 resultados
        try:
            # precio en formato " 42 €" o "€42"
            price_td = row.select_one("td.price")
            price_txt = price_td.get_text(" ", strip=True)
            price = int(re.sub(r"[^\d]", "", price_txt))

            # aerolínea: td.company title=...
            comp = row.select_one("td.company")
            airline = comp["title"] if comp and comp.has_attr("title") else comp.get_text(strip=True)

            # horas y duración en td.time: "07:00 – 08:50 (1 h 50 min)"
            time_txt = row.select_one("td.time").get_text(" ", strip=True)
            # dividimos en ["07:00", "–", "08:50", "(1", "h", "50", "min)"]
            parts = time_txt.split()
            dep_time = parts[0]
            arr_time = parts[2]
            dur_match = re.search(r"(\d+)\s*h", time_txt)
            dur_h = int(dur_match.group(1)) if dur_match else None

            flights.append({
                "provider":    "Azair",
                "origin":      origin,
                "destination": dest,
                "travel_date": date,
                "price":       price,
                "airline":     airline or "Unknown",
                "departure":   dep_time,
                "arrival":     arr_time,
                "duration_h":  dur_h
            })
        except Exception:
            continue

    return flights

@app.route("/flights", methods=["GET"])
def flights():
    origin = request.args.get("origin", "").upper()
    dest   = request.args.get("destination", "").upper()
    date   = request.args.get("travel_date", "")  # YYYY-MM-DD

    if not (origin and dest and date):
        return jsonify({"error": "Missing parameters"}), 400

    try:
        url = build_url(origin, dest, date)
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        flights = parse_flights(resp.text, origin, dest, date)
    except Exception as e:
        app.logger.warning(f"Azair scrape error: {e}")
        flights = []

    return jsonify(flights)

@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "scraper2-azair running"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=4003)
