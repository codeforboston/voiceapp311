import requests
from flask import Flask, jsonify

app = Flask(__name__)

#intents
#


@app.route('/')
def index():
    return "Hello World!";

@app.route('/app/v1/request')
def request():
    url = "https://data.cityofboston.gov/resource/cp2t-tvxx.json"

    headers = {
     
        'cache-control': "no-cache"
        }
    response = requests.get(url, headers=headers)
    json_data = response.json()

    parsed_data = []
    for entry in json_data[:]:
        parsed_data.append({
            'recycling':entry["recycling"],
            'trash': entry["trash"],
        })
    return jsonify({'foo':json_data})

if __name__ == '__main__':
    app.run(debug=True)