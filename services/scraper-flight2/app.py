from flask import Flask, request, jsonify
app = Flask(__name__)

@app.route('/flights', methods=['GET'])
def get_flights():
    origin = request.args.get('origin')
    destination = request.args.get('destination')
    travel_date = request.args.get('travel_date')
    return jsonify([
        {'provider':'Scraper2-Sky','origin':origin,'destination':destination,'travel_date':travel_date,'price':140}
    ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4003)