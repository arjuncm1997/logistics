from logistic import app,db




class Materials(db.Model):
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(200))
    brand = db.Column(db.String(200))
    avail = db.Column(db.String(200))
    price = db.Column(db.String(200))
    place = db.Column(db.String(200))
    image = db.Column(db.String(20), nullable=False, default='default.jpg')

    def __repr__(self):
        return f"Materials('{self.name}', '{self.brand}','{self.avail}', '{self.price}','{self.image}')"