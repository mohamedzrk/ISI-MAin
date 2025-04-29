from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Comparador de Vuelos</title>
</head>
<body style="padding: 20px;">
    <h1>Comparador de Vuelos</h1>
    <form method="get">
        <input name="ori" placeholder="Origen" value="{{ ori or '' }}" />
        <input name="dst" placeholder="Destino" value="{{ dst or '' }}" />
        <input type="date" name="date" value="{{ date or '' }}" />
        <button type="submit">Buscar</button>
    </form>
    <ul>
    {% for flight in flights %}
        <li>{{ flight['proveedor'] }} {{ flight['ori'] }}→{{ flight['dst'] }} {{ flight['date'] }} {{ flight['price'] }}€</li>
    {% endfor %}
    </ul>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    ori = request.args.get('ori')
    dst = request.args.get('dst')
    date = request.args.get('date')
    flights = []

    if ori and dst and date:
        try:
            response = requests.get('http://api-gateway:3001/flights', params={'ori': ori, 'dst': dst, 'date': date})
            if response.status_code == 200:
                flights = response.json()
        except Exception as e:
            print(f"Error fetching flights: {e}")

    return render_template_string(HTML_TEMPLATE, ori=ori, dst=dst, date=date, flights=flights)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
