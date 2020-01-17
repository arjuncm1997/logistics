import os
from flask import Flask
from flask import render_template, flash, redirect, request, abort, url_for
from logistic import app,db
from logistic.forms import Material
from logistic.models import Materials
from random import randint
from werkzeug.utils import secure_filename


@app.route('/')
def index():
    mat = Materials.query.all()
    return render_template("index.html",mat=mat)

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/uindex')
def uindex():
    return render_template("uindex.html")

@app.route('/admin')
def admin():
    return render_template("admin.html")

@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")

@app.route('/sindex')
def sindex():
    return render_template("sindex.html")

@app.route('/s_addmaterials',methods=['GET', 'POST'])
def s_addmaterials():
    image=""
    if request.method == 'POST':
        name1 = request.form['name']
        image = request.files['pic']
        asd  = Materials(name=name1, image=image)
        
        try:
            db.session.add(asd)
            db.session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
        
        if image:
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))    
    return render_template("s_addmaterials.html")



