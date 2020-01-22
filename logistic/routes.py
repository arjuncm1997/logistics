import os
from flask import Flask
from flask import render_template, flash, redirect, request, abort, url_for
from logistic import app,db, bcrypt
from logistic.forms import Material, RegistrationForm, LoginForm, Offers, Materialedit,Reject, Cart, Cart1,Purchaseview, Cartaddress, Cod
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
    material = Materials.query.filter_by(status='approved').all()
    return render_template("uindex.html",material=material)




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
    
        material = Materials(sowner= current_user.username,name=form.name.data,brand=form.brand.data,place=form.place.data,price = form.price.data,avail=form.avail.data,image=view, status='...')
       
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
    material = Materials.query.filter_by( status= '...').all()
    return render_template("amaterialsview.html",material = material)


@app.route('/amaterialsedit/<int:id>', methods=['GET', 'POST'])
def amaterialsedit(id):
    material = Materials.query.get_or_404(id)
    
    form = Materialedit()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            material.image = picture_file
        material.name = form.name.data
        material.brand = form.brand.data
        material.price = form.price.data
        material.place = form.place.data
        material.avail = form.avail.data
        material.status = 'approved'
        material.reason = ''
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/admin')
    elif request.method == 'GET':
        form.name.data = material.name
        form.brand.data = material.brand
        form.price.data = material.price
        form.place.data = material.place
        form.avail.data = material.avail
        form.owner.data = material.sowner

    image_file = url_for('static', filename='pics/' + material.image)
    return render_template('amaterialsedit.html',form=form, material=material)


@app.route('/aapprovedmaterials')
def aapprovedmaterials():
    material = Materials.query.filter_by( status= 'approved').all()
    return render_template("aapprovedmaterials.html",material = material)


@app.route('/aapprovededit/<int:id>', methods=['GET', 'POST'])
def aapprovededit(id):
    material = Materials.query.get_or_404(id)
    
    form = Materialedit()
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
        return redirect('/')
    elif request.method == 'GET':
        form.name.data = material.name
        form.brand.data = material.brand
        form.price.data = material.price
        form.place.data = material.place
        form.avail.data = material.avail
        form.owner.data = material.sowner

    image_file = url_for('static', filename='pics/' + material.image)
    return render_template('aapprovededit.html',form=form, material=material)







@app.route('/areject/<int:id>', methods=['GET', 'POST'])
def areject(id):
    material = Materials.query.get_or_404(id)
    
    form = Reject()
    if form.validate_on_submit():
        material.reason = form.reject.data
        material.status = 'rejected'
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/admin')
    elif request.method == 'GET':
        form.reject.data = material.reason
    return render_template('areject.html',form=form, material=material)


@app.route('/umaterialprofile/<int:id>', methods=['GET', 'POST'])
def umaterialprofile(id):
    form=Cart()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.cart = 'added'
        db.session.commit()
        flash('Material added to Cart', 'success')
        return redirect('/uindex')
    return render_template("umaterialprofile.html",material = material, form= form)

@app.route('/ucart',methods = ['GET','POST'])
def ucart():
    form = Cart1()
    material = Materials.query.filter_by(cart = 'added').all()
    
    return render_template("ucart.html",material=material, form=form)


@app.route('/ucartto/<int:id>', methods = ['GET','POST'])
def ucartto(id):
    form = Cart1()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.uquantity = form.value.data
        material.utotalprice = int(material.price) * int(material.uquantity)
        db.session.commit()
        return redirect('/ucartaddress/'+str(material.id))
    return render_template("ucart.html", form=form)

@app.route('/ucartremove/<int:id>')
def ucartremove(id):
    remove = Materials.query.get_or_404(id)
    try:
        db.session.delete(remove)
        db.session.commit()
        return redirect('/ucart')
    except:
        return 'There was a problem removing that task'


@app.route('/ucartadd/<int:id>')
def ucartadd(id):
    add = Materials.query.get_or_404(id)
    material = Materials(uowner = current_user.username,cart = 'added',status = 'rejected' ,name= add.name,sowner = add.sowner,brand = add.brand,avail = add.avail,price = add.price,place = add.place,image = add.image,reason = add.reason,desc = add.desc,uquantity = add.uquantity,upayment = add.upayment,utotalprice =add.utotalprice,uname = add.uname,uaddress = add.uaddress)
    db.session.add(material)
    db.session.commit()
    flash('added to your cart')
    return redirect('/uindex')


    


@app.route('/ucartaddress/<int:id>', methods = ['GET','POST'])
def ucartaddress(id):
    form = Cartaddress()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.uname = form.name.data
        material.uaddress = form.address.data
        db.session.commit()
        return redirect('/upayment/'+str(material.id))
    return render_template('/ucartaddress.html',mat = material,form=form)

@app.route('/upayment/<int:id>')
def upayment(id):
    form = Cod()
    material = Materials.query.get_or_404(id)
    return render_template('upayment.html',material = material,form=form)


@app.route('/cod/<int:id>',methods = ['GET','POST'])
def cod(id):
    form = Cod()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.upayment = 'cod'
        material.cart = 'removed'
        db.session.commit()
        return redirect('/successful')
    return render_template('/ucartaddress.html',mat = material,form=form)
    
@app.route('/successful')
def successful():
    return render_template("successful.html")


@app.route('/apurchasematerial')
def apurchasematerial():
    form =Purchaseview()
    material = Materials.query.filter_by(upayment="cod").all()
    return render_template("apurchasematerial.html",material = material,form=form)


@app.route('/delivery/<int:id>',methods=['GET','POST'])
def delivery(id):
    form = Purchaseview()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.deliverystatus = form.name.data
        db.session.commit()
        return redirect('/apurchasematerial')
    return render_template('/apurchasematerial.html',form=form)
