from flask import Flask, render_template, request, jsonify
from forms.Forms import AmenityForm

import csv
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from parts import calculate
from parts import Location

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "amenities.csv")

app = Flask(__name__)
app.secret_key = 'supersecretkey'

current_amenity = "bench"
# Global variable to store the latest location
latest_location = {'latitude': None, 'longitude': None}


@app.route('/', methods=['GET', 'POST'])
def home():
    global current_amenity

    objects = []
    with open(CSV_PATH, mode='r', newline='') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            objects.append(row[0])

    form = AmenityForm()
    form.name.choices = objects

    if form.validate_on_submit():
        current_amenity = str(form.name.data)
        print("Amenity set to:", current_amenity)

    return render_template('index.html', objects=objects, form=form)


@app.route('/fetch_distance')
def fetch_distance():
    if current_amenity is None:
        return "Bitte wähle etwas aus"

    try:
        amenity_data = Location.get_nearest_amenity(current_amenity)
        if amenity_data is None:
            return jsonify({"error": "Keine Daten verfügbar"}), 500

        dist = calculate.calculate_distance(amenity_data)
        return jsonify({"distance": dist})
    except Exception as e:
        print(f"Error in fetch_distance: {e}")
        return jsonify({"error": str(e)}), 500


@app.route('/get_amenity')
def get_amenity():
    return jsonify({"amenity": current_amenity or "bench"})


# ---------------- NEW ROUTES ----------------

@app.route('/set_location', methods=['POST'])
def set_location():
    global latest_location
    try:
        data = request.get_json()
        latitude = data.get('latitude')
        longitude = data.get('longitude')

        print(f"Received location - Lat: {latitude}, Lon: {longitude}")

        # Store location in global variable
        latest_location['latitude'] = latitude
        latest_location['longitude'] = longitude

        return jsonify({
            'status': 'success',
            'message': 'Location received',
            'latitude': latitude,
            'longitude': longitude
        }), 200

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 400


@app.route('/get_location', methods=['GET'])
def get_location():
    if latest_location['latitude'] is None or latest_location['longitude'] is None:
        return jsonify({
            'status': 'error',
            'message': 'No location set yet'
        }), 404

    return jsonify({
        'status': 'success',
        'latitude': latest_location['latitude'],
        'longitude': latest_location['longitude']
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
