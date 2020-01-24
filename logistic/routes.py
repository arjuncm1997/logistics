import os
from flask import Flask
from flask import render_template, flash, redirect, request, abort, url_for
from logistic import app,db, bcrypt, mail
from logistic.forms import Material, RegistrationForm, LoginForm, Offers,Account ,Changepassword,Reset,Changepassword, Materialedit,Reject,Paypal, Creditcard,Cart, Cart1,Purchaseview, Cartaddress, Cod
from logistic.models import Materials, Login, Offer,Credit, Pay, Contact
from random import randint
from PIL import Image
from flask_login import login_user, current_user, logout_user, login_required
from flask_mail import Message

@app.route('/')
def index():
    material = Materials.query.filter_by(status='approved',offer='no').all()
    material2 = Materials.query.filter_by(status='approved',offer='added').all()
    return render_template("index.html",material=material,material2 = material2)



@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/uindex')
@login_required
def uindex():
    material = Materials.query.filter_by(status='approved',offer='no').all()
    material2 = Materials.query.filter_by(status='approved',offer='added').all()
    return render_template("uindex.html",material=material,material2 = material2)




@app.route('/admin')
@login_required
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
@login_required
def sindex():
    return render_template("sindex.html")

@app.route('/s_addmaterials',methods=['GET', 'POST'])
@login_required
def s_addmaterials():
    form=Material()
    if form.validate_on_submit():
        if form.pic.data:
            pic_file = save_picture(form.pic.data)
            view = pic_file
        print(view)  
    
        material = Materials(sowner= current_user.username,name=form.name.data,brand=form.brand.data,desc = form.desc.data, place=form.place.data,price = form.price.data,avail=form.avail.data,image=view, status='...')
       
        db.session.add(material)
        db.session.commit()
        flash('materials added')
        return redirect('/sindex')
            
    
    return render_template("s_addmaterials.html",form=form)

@app.route('/smaterialsview')
@login_required
def smaterialsview():
    material = Materials.query.filter_by(sowner=current_user.username)
    return render_template("smaterialsview.html",mat=material)


@app.route('/smaterialsedit/<int:id>', methods=['GET', 'POST'])
@login_required
def smaterialsedit(id):
    material = Materials.query.get_or_404(id)
    
    form = Material()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            material.image = picture_file
        material.name = form.name.data
        material.brand = form.brand.data
        material.desc = form.desc.data
        material.price = form.price.data
        material.place = form.place.data
        material.avail = form.avail.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/smaterialsview')
    elif request.method == 'GET':
        form.name.data = material.name
        form.brand.data = material.brand
        form.desc.data = material.desc
        form.price.data = material.price
        form.place.data = material.place
        form.avail.data = material.avail

    image_file = url_for('static', filename='pics/' + material.image)
    return render_template('smaterialsedit.html',form=form, material=material)


@app.route('/delete/<int:id>')
def delete(id):
    delet = Materials.query.get_or_404(id)

    try:
        db.session.delete(delet)
        db.session.commit()
        return redirect('/smaterialsview')
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
@login_required
def amaterialsview():
    material = Materials.query.filter_by( status= '...').all()
    return render_template("amaterialsview.html",material = material)


@app.route('/amaterialsedit/<int:id>', methods=['GET', 'POST'])
@login_required
def amaterialsedit(id):
    material = Materials.query.get_or_404(id)
    
    form = Materialedit()
    if form.validate_on_submit():
        material.name = form.name.data
        material.brand = form.brand.data
        material.price = form.price.data
        material.place = form.place.data
        material.avail = form.avail.data
        material.status = 'approved'
        material.reason = ''
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/amaterialsview')
    elif request.method == 'GET':
        form.name.data = material.name
        form.brand.data = material.brand
        form.price.data = material.price
        form.place.data = material.place
        form.avail.data = material.avail
        form.owner.data = material.sowner

    return render_template('amaterialsedit.html',form=form, material=material)


@app.route('/aapprovedmaterials')
@login_required
def aapprovedmaterials():
    material = Materials.query.filter_by( status= 'approved').all()
    return render_template("aapprovedmaterials.html",material = material)


@app.route('/aapprovededit/<int:id>', methods=['GET', 'POST'])
@login_required
def aapprovededit(id):
    material = Materials.query.get_or_404(id)
    
    form = Materialedit()
    if form.validate_on_submit():
        material.name = form.name.data
        material.brand = form.brand.data
        material.price = form.price.data
        material.offerprice = form.offerprice.data
        material.place = form.place.data
        material.avail = form.avail.data
        db.session.commit()
        flash('Your post has been updated!', 'success')
        return redirect('/admins')
    elif request.method == 'GET':
        form.name.data = material.name
        form.brand.data = material.brand
        form.price.data = material.price
        form.offerprice.data = material.offerprice
        form.place.data = material.place
        form.avail.data = material.avail
        form.owner.data = material.sowner

    return render_template('aapprovededit.html',form=form, material=material)







@app.route('/areject/<int:id>', methods=['GET', 'POST'])
@login_required
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
@login_required
def umaterialprofile(id):
    form=Cart()
    material = Materials.query.get_or_404(id)
    return render_template("umaterialprofile.html",material = material, form= form)

@app.route('/ucart',methods = ['GET','POST'])
@login_required
def ucart():
    form = Cart1()
    material = Materials.query.filter_by(cart = 'added',uowner=current_user.username).all()
    
    return render_template("ucart.html",material=material, form=form)


@app.route('/ucartto/<int:id>', methods = ['GET','POST'])
@login_required
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
@login_required
def ucartremove(id):
    remove = Materials.query.get_or_404(id)
    try:
        db.session.delete(remove)
        db.session.commit()
        return redirect('/ucart')
    except:
        return 'There was a problem removing that task'


@app.route('/ucartadd/<int:id>')
@login_required
def ucartadd(id):
    add = Materials.query.get_or_404(id)
    material = Materials(uowner = current_user.username,cart = 'added',status = 'rejected' ,name= add.name,sowner = add.sowner,brand = add.brand,avail = add.avail,price =  add.offerprice,place = add.place,image = add.image,reason = add.reason,desc = add.desc,uquantity = add.uquantity,upayment = add.upayment,utotalprice =add.utotalprice,uname = add.uname,uaddress = add.uaddress)
    db.session.add(material)
    db.session.commit()
    flash('added to your cart')
    return redirect('/uindex')

@app.route('/ucartadd1/<int:id>')
@login_required
def ucartadd1(id):
    add = Materials.query.get_or_404(id)
    material = Materials(uowner = current_user.username,cart = 'added',status = 'rejected' ,name= add.name,sowner = add.sowner,brand = add.brand,avail = add.avail,price =  add.price,place = add.place,image = add.image,reason = add.reason,desc = add.desc,uquantity = add.uquantity,upayment = add.upayment,utotalprice =add.utotalprice,uname = add.uname,uaddress = add.uaddress)
    db.session.add(material)
    db.session.commit()
    flash('added to your cart')
    return redirect('/uindex')


    


@app.route('/ucartaddress/<int:id>', methods = ['GET','POST'])
@login_required
def ucartaddress(id):
    form = Cartaddress()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.uname = form.name.data
        material.uphone = form.phone.data
        material.uaddress = form.address.data
        db.session.commit()
        return redirect('/upayment/'+str(material.id))
    return render_template('/ucartaddress.html',mat = material,form=form)

@app.route('/upayment/<int:id>')
@login_required
def upayment(id):
    form = Cod()
    form1 = Creditcard()
    form2 = Paypal()
    material = Materials.query.get_or_404(id)
    return render_template('upayment.html',material = material,form=form,form1 =form1,form2=form2)


@app.route('/cod/<int:id>',methods = ['GET','POST'])
@login_required
def cod(id):
    form = Cod()
    form1 = Creditcard()
    form2 = Paypal()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.upayment = 'cod'
        material.purchase = 'purchased'
        material.cart = 'removed'
        sendmail()
        db.session.commit()
        return redirect('/successful')
    return render_template('/upayment.html',mat = material,form=form, form1 =form1,form2=form2)

def sendmail():
    msg = Message('successful',
                  recipients=[current_user.email])
    msg.body = f''' your Order Succsessfully Completed...   Track Your Order   'http://127.0.0.1:5000/login' '''
    mail.send(msg)

@app.route('/creditcard/<int:id>',methods = ['GET','POST'])
@login_required
def creditcard(id):
    form = Cod()
    form1 = Creditcard()
    form2 = Paypal()
    material = Materials.query.get_or_404(id)
    if form1.validate_on_submit():
        material.upayment = 'credit card'
        material.purchase = 'purchased'
        material.cart = 'removed'
        sendmail()
        db.session.commit()
    if form1.validate_on_submit():
        credit = Credit(userid = material.id,username = material.name,name = form1.name.data,card= form1.number.data ,cvv=form1.cvv.data , expdate=form1.date.data)
        db.session.add(credit)
        db.session.commit()
        return redirect('/successful1')
    return render_template('/upayment.html',form=form ,form1 =form1,form2=form2)

@app.route('/paypal/<int:id>',methods = ['GET','POST'])
@login_required
def paypal(id):
    form = Cod()
    form1 = Creditcard()
    form2 = Paypal()
    material = Materials.query.get_or_404(id)
    if form2.validate_on_submit():
        material.upayment = 'Paypal'
        material.purchase = 'purchased'
        material.cart = 'removed'
        sendmail()
        db.session.commit()
    if form2.validate_on_submit():
        pay = Pay(userid = material.id,username = material.name,name = form2.name.data,card= form2.number.data ,cvv=form2.cvv.data , validdate=form2.date.data)
        db.session.add(pay)
        db.session.commit()
        return redirect('/successful1')
    return render_template('/upayment.html',form=form ,form1 =form1,form2=form2)
    
@app.route('/successful')
@login_required
def successful():
    return render_template("successful.html")

@app.route('/successful1')
@login_required
def successful1():
    return render_template("successful1.html")


@app.route('/apurchasematerial')
@login_required
def apurchasematerial():
    form =Purchaseview()
    material = Materials.query.filter_by(purchase = 'purchased').all()
    return render_template("apurchasematerial.html",material = material,form=form)


@app.route('/delivery/<int:id>',methods=['GET','POST'])
@login_required
def delivery(id):
    form = Purchaseview()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit():
        material.deliverystatus = form.name.data
        db.session.commit()
        return redirect('/apurchasematerial')
    return render_template('/apurchasematerial.html',form=form)


@app.route('/umyorder')
@login_required
def umyorder():
    material = Materials.query.filter_by(uowner = current_user.username,upayment='cod').all()
    return render_template("umyorder.html",material=material)


@app.route('/aoffer')
@login_required
def aoffer():
    form = Purchaseview()
    material = Materials.query.filter_by( status= 'approved').all()
    return render_template("aoffer.html",material = material,form=form)

@app.route('/aofferadd/<int:id>',methods = ['GET','POST'])
@login_required
def aofferadd(id):
    form = Purchaseview()
    material = Materials.query.get_or_404(id)
    if form.validate_on_submit:
        material.offerprice = form.name.data
        material.offer = 'added'
        dis= int(material.price)- int(material.offerprice)
        material.discount = dis
        db.session.commit()
        flash ("offer added")
        return redirect('/aoffer')
    elif request.method == 'GET':
        form.name.data = material.offerprice
    return render_template('/aoffer.html',form=form,material = material)

@app.route('/aofferview')
@login_required
def aofferview():
    material = Materials.query.filter_by(offer='added').all()
    return render_template("aofferview.html",material=material)


@app.route('/offerremove/<int:id>')
def offerremove(id):
    remove = Materials.query.get_or_404(id)
    remove.offer = 'no'
    remove.offerprice = 'NULL'
    remove.discount = 'NULL'
    db.session.commit()
    return redirect("/aofferview")



@app.route("/uaccount/<int:id>", methods=['GET', 'POST'])
@login_required
def uaccount(id):
    form = Account()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            current_user.image = picture_file
        current_user.username = form.name.data
        current_user.email = form.email.data
        db.session.commit() 
    elif request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image)
    return render_template('uaccount.html', title='Account', image_file=image_file, form=form)

@app.route("/saccount/<int:id>", methods=['GET', 'POST'])
@login_required
def saccount(id):
    form = Account()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            current_user.image = picture_file
        current_user.username = form.name.data
        current_user.email = form.email.data
        db.session.commit() 
    elif request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image)
    return render_template('saccount.html', title='Account', image_file=image_file, form=form)


@app.route('/sfeedback',methods=['GET', 'POST'])
@login_required
def sfeedback():
    if request.method=='POST':
        subject= request.form['subject']
        message= request.form['message']
        
        new = Contact(name=current_user.username, email = current_user.email,subject =subject,message=message,usertype = 'seller')
        try:
            db.session.add(new)
            db.session.commit()
            return redirect('/sindex')

        except:
            return 'not add'  
    else:
        return render_template("sfeedback.html")


@app.route('/ufeedback',methods=['GET', 'POST'])
@login_required
def ufeedback():
    if request.method=='POST':
        subject= request.form['subject']
        message= request.form['message']
        
        new = Contact(name=current_user.username, email = current_user.email,subject =subject,message=message,usertype = 'user')
        try:
            db.session.add(new)
            db.session.commit()
            return redirect('/uindex')

        except:
            return 'not add'  
    else:
        return render_template("ufeedback.html")


@app.route('/contact',methods=['GET', 'POST'])
def contact():
    if request.method=='POST':
        name= request.form['name']
        email= request.form['email']
        subject= request.form['subject']
        message= request.form['message']
        
        new = Contact(name=name, email = email,subject =subject,message=message,usertype = 'public')
        try:
            db.session.add(new)
            db.session.commit()
            return redirect('/')

        except:
            return 'not add'  
    else:
        return render_template("contact.html")


@app.route('/auserfeedback')
@login_required
def auserfeedback():
    feedback = Contact.query.filter_by(usertype='user').all()
    return render_template("auserfeedback.html",feedback=feedback)

@app.route('/asellerfeedback')
@login_required
def asellerfeedback():
    feedback = Contact.query.filter_by(usertype='seller').all()
    return render_template("asellerfeedback.html",feedback=feedback)

@app.route('/apublicfeedback')
@login_required
def apublicfeedback():
    feedback = Contact.query.filter_by(usertype='public').all()
    return render_template("apublicfeedback.html",feedback=feedback)


@app.route('/aprofile/<int:id>',methods=['GET','POST'])
@login_required
def aprofile(id):
    form = Account()
    if form.validate_on_submit():
        if form.pic.data:
            picture_file = save_picture(form.pic.data)
            current_user.image = picture_file
        current_user.username = form.name.data
        current_user.email = form.email.data
        db.session.commit() 
    elif request.method == 'GET':
        form.name.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='pics/' + current_user.image)
    return render_template("aprofile.html",form= form)


@app.route('/auserview')
def auserview():
    user = Login.query.filter_by(usertype='user').all()
    return render_template("auserview.html",user=user)

@app.route('/asellerview')
def asellerview():
    user = Login.query.filter_by(usertype='seller').all()
    return render_template("asellerview.html",user=user)

@app.route('/changepassword', methods=['GET', 'POST'])
def changepassword():
    form = Changepassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        db.session.commit()
        logout_user()
        flash('Your Password Has Been Changed')
        return redirect('/login') 
    return render_template('changepassword.html', form=form)







def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message('Password Reset Request',
                  recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link:
{url_for('resettoken', token=token, _external=True)}

If you did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)






@app.route('/resetrequest', methods=['GET','POST'])
def resetrequest():
    form = Reset()
    if form.validate_on_submit():
        user = Login.query.filter_by(email=form.email.data).first()
        send_reset_email(user)
        flash('An email has been sent with instructions to reset your password.', 'info')
        return redirect('/login')
    return render_template("resetrequest.html",form = form)


@app.route("/resetpassword/<token>", methods=['GET', 'POST'])
def resettoken(token):
    user = Login.verify_reset_token(token)
    if user is None:
        flash('That is an invalid or expired token', 'warning')
        return redirect('/resetrequest')
    form = Changepassword()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in', 'success')
        return redirect('/login')
    return render_template('resetpassword.html', title='Reset Password', form=form)