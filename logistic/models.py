from logistic import app,db, login_manager
from flask_login import UserMixin
from flask_table import Table, Col, LinkCol
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

@login_manager.user_loader
def load_user(id):
    return Login.query.get(int(id))


class Login(db.Model, UserMixin):
    id=db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    usertype = db.Column(db.String(80), nullable=False)

class Materials(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    sowner = db.Column(db.String)
    uowner = db.Column(db.String)
    name = db.Column(db.String(200))
    brand = db.Column(db.String(200))
    avail = db.Column(db.String(200))
    price = db.Column(db.String(200))
    offerprice = db.Column(db.String(200))
    discount = db.Column(db.String(200))
    place = db.Column(db.String(200))
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
    status = db.Column(db.String(200))
    reason = db.Column(db.String(200))
    cart = db.Column(db.String(200))
    desc = db.Column(db.String(200))
    uquantity = db.Column(db.String(200))
    upayment = db.Column(db.String(200))
    utotalprice = db.Column(db.String(200))
    uname = db.Column(db.String((200)))
    uaddress = db.Column(db.String((200)))
    deliverystatus = db.Column(db.String(220))
    offer = db.Column(db.String(220),default='no')
    purchase = db.Column(db.String(220))

    def __repr__(self):
        return f"Materials('{self.name}', '{self.brand}','{self.avail}', '{self.price}','{self.image}')"



class Offer(db.Model,UserMixin):
    id = db.Column(db.Integer,primary_key=True)
    owner = db.Column(db.String)
    name = db.Column(db.String(40),unique=False,nullable=False)
    matname =  db.Column(db.String)
    disprice = db.Column(db.String)
    image = db.Column(db.String(20), nullable=False, default='default.jpg')
