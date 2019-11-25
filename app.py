from flask import Flask, render_template, flash, redirect, url_for, session, request, logging
from wtforms import Form, StringField, TextAreaField, PasswordField, validators, SelectField, IntegerField
from passlib.hash import sha256_crypt
import sqlite3
from functools import wraps
import datetime
import os
from werkzeug.utils import secure_filename

conn = sqlite3.connect('olx.db')

app = Flask(__name__)

UPLOAD_FOLDER = 'static'
ALLOWED_EXTENSIONS = set([ 'png', 'jpg', 'jpeg', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def home():
    return render_template('home3.html')


class RegisterForm(Form):
    name = StringField('Name', [validators.DataRequired('Please enter name'), validators.Length(min=1, max=50)])
    email = StringField('Email',[ validators.DataRequired('Please enter email'), validators.Length(min=6, max=50)])
    phone = StringField('Phone', [validators.DataRequired('Please enter phone number'), validators.Length(min=0, max=10)])
    password = PasswordField('Password',[validators.DataRequired('Please enter password!'),  validators.EqualTo('confirm', message='Passwords do not match')])
    confirm = PasswordField('Confirm Password')


@app.route("/register", methods=['GET' , 'POST'])
def register():
    conn = sqlite3.connect('olx.db')
    form= RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        phone = form.phone.data
        password = sha256_crypt.encrypt(str(form.password.data))
        c = conn.cursor()
        c.execute("INSERT INTO USERS(name, email,phone, password) VALUES(?,?,?,?)",(name, email,phone, password))
        conn.commit()
        c.close()

        flash('You are now registered and can log in', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Get Form Fields
        email = request.form['email']
        password_candidate = request.form['password']

        conn = sqlite3.connect('olx.db')
        c = conn.cursor()

        # Get user by username
        result = c.execute("SELECT * FROM users WHERE email = ?", [email])

        #if result > 0:
        if c is not None:
            data = c.fetchone()
            password = data[4] #3rd column in db
            name = data[1] #1st column in db
            email= data[2]
            # Compare Passwords
            if sha256_crypt.verify(password_candidate, password):
                # Passed
                session['logged_in'] = True
                session['name'] = name
                session['email']= email

                flash('You are now logged in', 'success')
                return redirect(url_for('home'))
            else:
                error = 'Invalid login'
                return render_template('login.html', error=error)
            # Close connection
        else:
            error = 'User not found'
            return render_template('login.html', error=error)
        c.close()

    return render_template('login.html')


def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap


@app.route('/dashboard')
@is_logged_in
def dashboard():
    conn = sqlite3.connect('olx.db')
    c = conn.cursor()
    c.execute("""SELECT * FROM category;""")
    category = c.fetchall()
    c.close()
    return render_template('dashboard.html', category=category)


@app.route('/dashboard/<category>', methods=['GET', 'POST'])
@is_logged_in
def chosen_category(category):
    conn = sqlite3.connect('olx.db')
    c = conn.cursor()
    c.execute('''select cat_id from category where CATEGORY_NAME=?;''', (category,))
    data = c.fetchone()
    print(data, "hiiiii")
    cat_id=data[0]
    c.execute("""SELECT * FROM items2 WHERE cat_id=?; """, (cat_id,))
    items = c.fetchall()
    print(items)
    c.close()
    return render_template('all_items.html', items=items, category=category)



@app.route('/dashboard-order/<item_id>')
@is_logged_in
def place_order(item_id):
    conn = sqlite3.connect('olx.db')
    c = conn.cursor()
    custname = session['name']
    customer_email= session['email']

    now = datetime.date.today()
    week = datetime.timedelta(days=7)
    delivery_date = now + week


    c.execute('''select price,name,owner_id, picture from items2 where item_id=?;''', (item_id,))
    data= c.fetchone()
    cost = data[0]
    item_name=data[1]
    ownerid=data[2]
    picture=data[3]

    c.execute('''select name, email, phone from users where user_id=?;''', (ownerid,))
    data = c.fetchone()
    ownname = data[0]
    ownemail = data[1]
    ownphone = data[2]

    c.execute('''select * from users where email=?;''', (customer_email,))
    data= c.fetchone()
    custid= data[0]

    c.execute('''insert into orders(owner_id, buyer_id, item_id, ord_date, cost) values (?,?,?,?,?);''',(ownerid,custid, item_id, now, cost))

    c.execute('''select * from orders order by order_id desc ;''')
    result= c.fetchone()
    cost= result[5]
    c.execute('''delete from items2 where item_id=?;''', (item_id,))
    flash('You have successfully placed your order!', 'success')

    return render_template('order_details.html', item_name=item_name, cost=cost, cust_data=data, delivery_date=delivery_date , ownname=ownname, ownemail=ownemail, ownphonw=ownphone, picture=picture)


@app.route('/logout')
@is_logged_in
def logout():
    session.clear()
    flash('You are now logged out!', 'success')
    return redirect(url_for('home'))


@app.route("/about")
def about():
    return render_template('about.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')


#-----------------------Admin----------------------
def is_admin_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'admin_logged_in' in session:
            return f(*args, *kwargs)
        else:
            return redirect(url_for('admin_login'))
    return wrap


class AddItem(Form):
    itemname = StringField('Item Name', [validators.DataRequired('Please enter name'), validators.Length(min=1, max=50)])
    category = SelectField('Category', choices=[('Furniture', 'Furniture'), ('Laptops', 'Laptops'), ('Mobiles', 'Mobiles')])
    howold = IntegerField('How Old (yrs)', [validators.DataRequired('Please enter how old it is')])
    cost= IntegerField('Cost', [validators.DataRequired('Please enter cost')])


@app.route('/sell' , methods=['GET','POST'])
@is_logged_in
def sellitem():
    name = session['name']
    conn = sqlite3.connect('olx.db')
    form = AddItem(request.form)
    if request.method == 'POST' and form.validate():
        itemname = form.itemname.data
        category = form.category.data
        howold=form.howold.data
        cost = form.cost.data
        image = request.files['image']
        if image and allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filename.replace('_', ' ')
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        c = conn.cursor()
        c.execute('''select user_id from users where NAME=?;''', (name,))
        own_id=c.fetchone()
        own_id=own_id[0]
        c.execute('''select cat_id from category where CATEGORY_NAME=?;''', (category,))
        data = c.fetchone()
        cat_id=data[0]
        filenamefinal="/static/"+filename
        print(filename)
        c.execute("insert into ITEMS2(NAME, CAT_ID, PRICE,HOW_OLD, OWNER_ID, PICTURE) values(?,?,?,?,?,?)",(itemname,cat_id,cost,howold,own_id,filenamefinal))

        conn.commit()
        flash('You have succesfully added the item!', 'success')
        return redirect(url_for('home'))
    return render_template('add-item.html', form=form)


@app.route('/admin/view_orders')
@is_admin_logged_in
def admin_view_orders():
    name = session['admin_name']
    conn = sqlite3.connect('mobileshopping.db')
    c = conn.cursor()
    c.execute('''select o.order_id, c.name, o.model, o.cost, d.name from orders o, customer c, deliveryboy d where o.cust_id=c.id and o.del_boy_id=d.id ;''')
    data=c.fetchall()

    return render_template('view-orders.html', orders=data)



#---------------Admin end---------------------------


if __name__ == "__main__":
    #createtable()
    app.secret_key="secret123"
    app.run(debug=True)


