from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, TextField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import current_user
from logistic.models import Materials





class Material(FlaskForm):
    name = StringField('Name',
                        validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    avail = StringField('Avail quantity')
    price = StringField('Price')
    place = StringField('Place')
    submit = SubmitField('Submit')