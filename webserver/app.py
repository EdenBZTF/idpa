from flask import Flask, render_template
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
    with open(file=CSV_PATH, mode='r') as f:
        reader = csv.reader(f, delimiter=',')
        for i in reader:
            objects.append(i[0])
    form = AmenityForm()
    form.name.choices = objects
    
    if form.validate_on_submit():
        print(form.name.data)
    
    return render_template('index.html', objects=objects, form=form)

@app.route('/fetch_distance')
def fetch_distance():
    distance =  random.randint(0,100)
    print(distance)
    return '{ "distance": ' + str(distance) + ' }'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
