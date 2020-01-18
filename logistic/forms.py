from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, TextField, validators
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from flask_login import current_user
from logistic.models import Materials, Login,Offer



class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_username(self, username):
        user = Login.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = Login.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')



class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Material(FlaskForm):
    name = StringField('Name',
                        validators=[DataRequired()])
    brand = StringField('Brand', validators=[DataRequired()])
    avail = StringField('Avail quantity')
    price = StringField('Price')
    place = StringField('Place')
    pic = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])
    submit = SubmitField('Submit')

class Offers(FlaskForm):
    name = StringField('Offer Name',
                        validators=[DataRequired()])
    price = StringField('Discount Price')
    pic = FileField('Upload Picture', validators=[FileAllowed(['jpg', 'png','jpeg'])])

    def get_all_materials():
        return Materials.query

    matname=QuerySelectField('Material Name',query_factory=get_all_materials,get_label="name")

    submit = SubmitField('Submit')