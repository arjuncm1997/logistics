from flask import Flask
from flask_wtf import FlaskForm,CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager

app=Flask(__name__)
app.config['SECRET_KEY'] = '8ea2a86e42689205dde0ba81f31138b6'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///logistic.db'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager(app)

from logistic import routes