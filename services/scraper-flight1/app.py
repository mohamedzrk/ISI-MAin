from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/flights', methods=['GET'])
def get_flights():
    # Extrae parámetros de consulta
    ori = request.args.get('ori')
    dst = request.args.get('dst')
    date = request.args.get('date')

    # Simula resultados "scrapeados" de proveedor 1
    flights = [
        {
            'proveedor': 'Scraper1-Air',
            'ori': ori,
            'dst': dst,
            'date': date,
            'price': 110
        }
    ]
    return jsonify(flights)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4002)
