from flask import Flask, render_template, session
from forms.Forms import AmenityForm 
import random
import csv
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "amenities.csv")
app = Flask(__name__)
app.secret_key = 'supersecretkey'  

@app.route('/', methods=['GET', 'POST'])
def home():
    objects = []
    # Read CSV and add "selected" column if missing
    amenities = []
    with open(CSV_PATH, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        if 'selected' not in fieldnames:
            fieldnames.append('selected')
        for row in reader:
            if 'selected' not in row:
                row['selected'] = '0'
            amenities.append(row)
            objects.append(row['name'])
    
    form = AmenityForm()
    form.name.choices = objects
    
    if form.validate_on_submit():
        set_amenity(str(form.name.data))
        update_csv_selection(str(form.name.data), amenities, fieldnames)
        print(get_amenity())
    
    return render_template('index.html', objects=objects, form=form)


@app.route('/fetch_distance')
def fetch_distance():
    distance = random.randint(0,100)
    print(distance)
    return '{ "distance": ' + str(distance) + ' }'

def set_amenity(n):
    session["amenity"] = n

def get_amenity():
    return session.get("amenity", "")

def update_csv_selection(selected_name, amenities, fieldnames):
    """Update CSV to mark the selected amenity."""
    for row in amenities:
        row['selected'] = '1' if row['name'] == selected_name else '0'
    
    with open(CSV_PATH, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(amenities)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
