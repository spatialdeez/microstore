import os
from flask import render_template, request, jsonify, flash, redirect, url_for, session
from app import app, db, ALLOWED_EXTENSIONS
from app.models import Product, Category, ProductForm, CategoryForm, LoginForm, RegistrationForm, User # import the database model
from werkzeug.utils import secure_filename

# frontpage index
@app.route('/')
def index():
    return render_template('index.html', page='Frontpage')

# user homepage
@app.route('/homepage')
def homepage():
    return render_template('homepage.html', page='homepage')

# show all products
@app.route('/products')
def products():
    products = Product.query.all()
    products_show = {}
    for product in products:
        products_show[product.id] =  {
            'name': product.name,
            'price': str(product.price), 
            'category': product.category.name, # category name
            'image_path': product.image_path
        }
    return render_template('product view.html', products_show=products_show)
    # return jsonify(products_show) # give all product lists

# show specific product details
@app.route('/product/<id>')
def product(id):
    product = Product.query.get_or_404(id)
    return f'product - {product.name} ${product.price}'

# show all categories
@app.route('/categories')
def categories():
    categories = Category.query.all()
    category_show = {}
    for category in categories:
        category_show[category.id] = {
            'name': category.name,
            }
        for product in category.products:
            category_show[category.id]['products'] = {
                'id': product.id,
                'name': product.name,
                'price': str(product.price),
            }
    return jsonify(category_show)

# show specific category details
@app.route('/product-create', methods=['GET', 'POST'])
def create_product():
    form = ProductForm()
    categories = [(c.id, c.name) for c in Category.query.all()]
    form.category.choices = categories
    
    def allowed_file(filename):
        return '.' in filename and filename.lower().rsplit('.', 1)[1] in ALLOWED_EXTENSIONS # check if file extension is allowed
    if form.validate_on_submit():
        name = form.name.data # get inputted name
        price = form.price.data # get inputted price
        category = Category.query.get_or_404(form.category.data) # get inputted category
        image = form.image.data # get uploaded image
        if allowed_file(image.filename):
            filename = secure_filename(image.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            if os.path.exists(filepath):
                flash('Product image already exists. Try changing the image name.', 'warning') # if image name already exists, redirect user back to the product create page
                return render_template('product create.html', form=form)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # store image into /static/images
        product = Product(name, price, category, filename) # stage the changes
        db.session.add(product) # add staged changes into current session
        db.session.commit() # commit staged changes
        flash(f'Product {name} has successfully been created!', 'success')
        return redirect(url_for('index')) # return user to frontpage
    
    if form.errors:
        flash(form.errors, 'danger') # show the error message
        
    return render_template('product create.html', form=form)

# create new category
@app.route('/category-create', methods=['GET','POST',])
def create_category():
    form = CategoryForm() # get the category create form

    if form.validate_on_submit(): # if form is submitted
        name = form.name.data # get inputted name
        category = Category(name=name) # stage new category name into the database
        db.session.add(category) # add staged changes
        db.session.commit() # commit staged changes
        flash(f'Category {str(name)} created successfully!', 'success') # show success flash message if category is successfully created
        return redirect(url_for('index'))
    if form.errors:
        flash(form.errors) # flash error if there is a problem

    return render_template('category create.html', form=form)

# delete product by id
@app.route('/product/<int:id>/delete', methods=['POST'])
def delete_product(id):
    product = Product.query.get_or_404(id) # show product or send back a 404 error
    
    # delete the image file if it exists
    if product.image_path:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], product.image_path)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    # delete the product from database
    db.session.delete(product)
    db.session.commit()
    
    flash(f'Product {product.name} has been deleted.', 'success')
    return redirect(url_for('products'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if session.get('username'):
        flash('You are already logged in', 'info')
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_username = User.query.filter(User.username.like('%' + username + '%')).first()
        if existing_username:
            flash('Username already taken. Try another one.', 'warning')
            return render_template('register.html')
        
        user = User(username, password) # stage changes
        db.session.add(user) # add staged changes into session
        db.session.commit() # commit session changes
        flash('Thank you for signing up as a user! Please try and log in now.', 'success')
        return redirect(url_for('login'))
    
    if form.errors:
        flash(form.errors)

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        existing_user = User.query.filter_by(username=username).first()
        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again', 'danger')
            return render_template('login.html', form=form)
        
        session['username'] = username
        flash(f'You have successfully logged in as {username}!', 'success')
        return redirect(url_for('index'))
    
    if form.errors:
        flash(form.errors)

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    if 'username' in session:
        session.pop('username')
        flash('You have logged out.', 'success')
    
    return redirect(url_for('index'))

