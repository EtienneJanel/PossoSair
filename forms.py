from flask_wtf import FlaskForm
from wtforms import SelectField
# from wtforms.validators import DataRequired, Length, EqualTo


class ConcelhosForm(FlaskForm):
    concelho = SelectField('concelho', choices=[])
    


