from flask import Flask, request, jsonify

app = Flask(__name__)

# Caché en memoria
cache = {}

@app.route('/cache', methods=['GET'])
def get_cache():
    # Extrae parámetros de consulta
    ori = request.args.get('ori')
    dst = request.args.get('dst')
    date = request.args.get('date')
    key = f"{ori}-{dst}-{date}"
    # Devuelve los datos guardados o lista vacía
    return jsonify(cache.get(key, []))

@app.route('/cache', methods=['POST'])
def post_cache():
    # Recibe JSON en body
    data_in = request.get_json()
    ori = data_in.get('ori')
    dst = data_in.get('dst')
    date = data_in.get('date')
    data = data_in.get('data')
    key = f"{ori}-{dst}-{date}"
    # Guarda en cache
    cache[key] = data
    return jsonify({'status': 'saved'})

@app.route('/')
def index():
    return 'Flight-cache está funcionando ✈️'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4004)
