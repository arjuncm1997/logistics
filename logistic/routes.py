import os
from flask import Flask
from flask import render_template, flash, redirect, request, abort, url_for
from logistic import app,db, bcrypt
from logistic.forms import Material, RegistrationForm, LoginForm, Offers
from logistic.models import Materials, Login, Offer
from random import randint
from PIL import Image
from flask_login import login_user, current_user, logout_user, login_required

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

@app.route('/login',methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Login.query.filter_by(email=form.email.data, usertype= 'seller').first()
        user1 = Login.query.filter_by(email=form.email.data, usertype= 'user').first()
        user2 = Login.query.filter_by(email=form.email.data, usertype= 'admin').first()
        if user and bcrypt.check_password_hash(user.password,form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/sindex')
        if user1 and bcrypt.check_password_hash(user1.password, form.password.data):
            login_user(user1, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/uindex')
        if user2 and user2.password== form.password.data:
            login_user(user2, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/admin')
        if user2 and bcrypt.check_password_hash(user2.password, form.password.data):
            login_user(user2, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect('/admin')

        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect('/')


@app.route('/registeruser', methods=['GET','POST'])
def registeruser():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new = Login(username= form.username.data,email=form.email.data, password=hashed_password, usertype= 'user' )
        db.session.add(new)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect('/')
    return render_template('registeruser.html',title='Register', form=form)

@app.route('/registerseller',methods=['GET','POST'])
def registerseller():
    form=RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new = Login(username= form.username.data,email=form.email.data, password=hashed_password, usertype= 'seller' )
        db.session.add(new)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect('/')

    return render_template("registerseller.html",form=form)

@app.route('/sindex')
def sindex():
    return render_template("sindex.html")

@app.route('/s_addmaterials',methods=['GET', 'POST'])
def s_addmaterials():
    form=Material()
    if form.validate_on_submit():
        if form.pic.data:
            pic_file = save_picture(form.pic.data)
            view = pic_file
        print(view)  
    
        material = Materials(name=form.name.data,brand=form.brand.data,place=form.place.data,price = form.place.data,avail=form.avail.data,image=view )
       
        db.session.add(material)
        db.session.commit()
        flash('materials added')
        return redirect('/sindex')
            
    
    return render_template("s_addmaterials.html",form=form)

@app.route('/smaterialsview')
def smaterialsview():
    material = Materials.query.all()
    return render_template("smaterialsview.html",mat=material)


@app.route('/smaterialsedit/<int:id>', methods=['GET', 'POST'])
def smaterialsedit(id):
    material = Materials.query.get_or_404(id)
    
    form = Material()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            material.image = picture_file
        material.name = form.name.data
        material.brand = form.brand.data
        material.price = form.price.data
        material.place = form.place.data
        material.avail = form.avail.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/smaterialsview')
    elif request.method == 'GET':
        form.name.data = material.name
        form.brand.data = material.brand
        form.price.data = material.price
        form.place.data = material.place
        form.avail.data = material.avail

    image_file = url_for('static', filename='pics/' + material.image)
    return render_template('smaterialsedit.html',form=form, material=material)


@app.route('/delete/<int:id>')
def delete(id):
    task_to_delet = Materials.query.get_or_404(id)

    try:
        db.session.delete(task_to_delet)
        db.session.commit()
        return redirect('/smaterialsview')
    except:
        return 'There was a problem deleting that task'




@app.route("/saddoffer",methods = ['GET','POST'])
def saddoffer():
    form=Offers()
    model=""
    if form.validate_on_submit():
        if form.pic.data:
            profile=save_picture(form.pic.data)
            model=profile

        material=form.matname.data
        offer = Offer(owner=current_user.username,name=form.name.data, matname=material.name,disprice=form.price.data,image=model )
        
        db.session.add(offer)
        db.session.commit()
        flash('offer has been created')
        return redirect('/sindex')
    return render_template('saddoffer.html',form=form ,title='New Offer',model=model)




@app.route('/sofferview')
def sofferview():
    offer = Offer.query.all()
    return render_template("sofferview.html",offer = offer)




@app.route('/sofferedit/<int:id>', methods=['GET', 'POST'])
def sofferedit(id):
    offer = Offer.query.get_or_404(id)
    
    form = Offers()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            material.image = picture_file
        offer.name = form.name.data
        offer.price = form.price.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/sofferview')
    elif request.method == 'GET':
        form.name.data = offer.name
        form.matname.data = offer.matname
        form.price.data = offer.disprice
    image_file = url_for('static', filename='pics/' + offer.image)
    return render_template('sofferedit.html',form=form, offer=offer)


@app.route('/offerdelete/<int:id>')
def offerdelete(id):
    task_to_delet = Offer.query.get_or_404(id)

    try:
        db.session.delete(task_to_delet)
        db.session.commit()
        return redirect('/sofferview')
    except:
        return 'There was a problem deleting that task'




def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

def save_picture(form_picture):
    random_hex = random_with_N_digits(14)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = str(random_hex) + f_ext
    picture_path = os.path.join(app.root_path, 'static/pics', picture_fn)
    
    output_size = (500, 500)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)
    return picture_fn




@app.route('/amaterialsview')
def amaterialsview():
    return render_template("amaterialsview.html")