from wtforms import SelectField, SubmitField
from flask_wtf import FlaskForm
from wtforms.fields.choices import SelectField
from wtforms.validators import InputRequired

class AmenityForm(FlaskForm):
    name = SelectField('Amenity', validators=[InputRequired()])
    submit = SubmitField('Submit')