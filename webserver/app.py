from flask import Flask, render_template
from forms.Forms import AmenityForm 
import random
import csv

app = Flask(__name__)
app.secret_key = 'supersecretkey'  

@app.route('/', methods=['GET', 'POST'])
def home():
    objects = []
    with open(file='amenities.csv', mode='r') as f:
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
    app.run(debug=True)
