import os
from functools import wraps
from flask import abort, render_template, flash, redirect, url_for, g, request
from flask_login import current_user, login_user, logout_user, login_required
from sqlalchemy.sql.expression import func
from app import app, db, login_manager, ALLOWED_EXTENSIONS
from app.models import Product, Category, User, Cart, CartItem, ProductForm, CategoryForm, LoginForm, RegistrationForm, AdminUserCreateForm, AdminUserUpdateform # import the database model and forms
from werkzeug.utils import secure_filename

# custom decorators
def admin_login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_admin():
            return abort(403)
        return func(*args, **kwargs)
    return decorated_view


# user initialisation
@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def get_current_user():
    g.user = current_user

# frontpage index
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('homepage'))
    return render_template('index.html', page_name='Frontpage')

# user homepage
@app.route('/homepage')
@login_required
def homepage():
    products = Product.query.order_by(func.random()).limit(9).all()
    products_show = {}
    for product in products:
        products_show[product.id] =  {
            'name': product.name, # product name
            'price': str(product.price), # product price
            'category': product.category.name, # category name
            'image_path': product.image_path # string of image name
        }
    return render_template('homepage.html', page_name='Homepage', products_show=products_show)

# show all products
@app.route('/products')
@app.route('/products/<int:page>')
def products(page=1):
    per_page = 3
    product_query = Product.query.order_by(Product.category_id, Product.price).all()
    pagination = Product.query.paginate(page=page, per_page=per_page, error_out=False)
    products = pagination.items
    products_show = {}
    for product in products:
        products_show[product.id] =  {
            'name': product.name, # product name
            'price': str(product.price), # product price
            'category': product.category.name, # category name
            'image_path': product.image_path # string of image name
        }
    return render_template('product view.html', page_name='Products', products_show=products_show, per_page=per_page, pagination=pagination)
    # return jsonify(products_show) # give all product lists

# show specific product details
@app.route('/product/<id>')
def product(id):
    product = Product.query.get_or_404(id)
    products_show = {}
    products_show[product.id] =  {
            'name': product.name,
            'price': str(product.price), 
            'category': product.category.name, # category name
            'image_path': product.image_path
        }
    return render_template('product view.html', page_name=f'{product.name}' ,products_show=products_show)

# show all categories
@app.route('/admin/categories')
@login_required
@admin_login_required
def categories_list_admin():
    categories = Category.query.all()
    category_data = []
    for category in categories:
        product_count = category.products.count()
        category_data.append({
            'id': category.id,
            'name': category.name,
            'product_count': product_count
        })
    return render_template('category edit.html', categories=category_data)

# show specific category details
@app.route('/product-create', methods=['GET', 'POST'])
@login_required
@admin_login_required
def create_product():
    form = ProductForm()
    categories = [(c.id, c.name) for c in Category.query.all()] # get all categories by id and name and put it into a list
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
                return render_template('product create.html', page_name='Create a product',form=form)
            image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename)) # store image into /static/images
        product = Product(name, price, category, filename) # stage the changes
        db.session.add(product) # add staged changes into current session
        db.session.commit() # commit staged changes
        flash(f'Product {name} has successfully been created!', 'success')
        return redirect(url_for('index')) # return user to frontpage
    
    if form.errors:
        flash(form.errors, 'danger') # show the error message
        
    return render_template('product create.html', page_name='Create a product', form=form)

# create new category
@app.route('/category-create', methods=['GET','POST',])
@login_required
@admin_login_required
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

    return render_template('category create.html', page_name='Create a category', form=form)

# delete product by id
@app.route('/product/<int:id>/delete', methods=['POST'])
@login_required
@admin_login_required
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

# delete category by id
@app.route('/category/<int:id>/delete', methods=['POST'])
@login_required
@admin_login_required
def delete_category(id):
    category = Category.query.get_or_404(id)
    
    # Check if category has products
    product_count = category.products.count()
    if product_count > 0:
        flash(f'Cannot delete category "{category.name}" because it has {product_count} product(s) associated with it. Please reassign or delete the products first.', 'danger')
        return redirect(url_for('categories_list_admin'))
    
    category_name = category.name
    db.session.delete(category) # delete category
    db.session.commit() # commit changes
    
    flash(f'Category {category_name} has been deleted successfully.', 'success')
    return redirect(url_for('categories_list_admin'))

@app.route('/cart')
@login_required
def view_cart():
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    # create a new cart if it is a new user
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
    cart_items = cart.get_items()
    return render_template('cart view.html', cart_items=cart_items)

@app.route('/cart/purchase/<int:id>', methods=['POST'])
@login_required
def purchase(id):
    product = Product.query.get_or_404(id) # obtain the product
    cart = Cart.query.filter_by(user_id=current_user.id).first()
    # create a cart if it is a new user
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.session.add(cart)
        db.session.commit()
        
    cart.add_item(product, quantity=1)
    db.session.commit()
    flash(f'Successfully added {product.name} into cart.', 'success')
    return redirect(url_for('view_cart'))


# register new users
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash('You are already logged in', 'info')
        return redirect(url_for('index'))
    
    form = RegistrationForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        admin = False
        existing_username = User.query.filter(User.username.like('%' + username + '%')).first()
        if existing_username:
            flash('Username already taken. Try another one.', 'warning')
            return render_template('register.html', page_name='Register', form=form)
        
        user = User(username, password, admin) # stage changes
        db.session.add(user) # add staged changes into session
        db.session.commit() # commit session changes
        flash('Thank you for signing up as a user! Please try and log in now.', 'success')
        return redirect(url_for('login'))
    
    if form.errors:
        flash(form.errors)

    return render_template('register.html', page_name='Register', form=form)

# log in user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = request.form.get('username')
        password = request.form.get('password')
        remember_me = request.form.get('remember-me')
        existing_user = User.query.filter_by(username=username).first()
        if not (existing_user and existing_user.check_password(password)):
            flash('Invalid username or password. Please try again', 'danger')
            return render_template('login.html', page_name='Log In', form=form)
        
        # check if checkbox is ticked
        if remember_me is None:
            remember_me = False
        else:
            remember_me = True

        login_user(existing_user, remember=remember_me)
        flash(f'You have successfully logged in as {username}!', 'success') 
        return redirect(url_for('index'))
    
    if form.errors:
        flash(form.errors)

    return render_template('login.html', page_name='Log In', form=form)

# log out user
@app.route('/logout')
@login_required
def logout():
    logout_user()    
    return redirect(url_for('index'))



# ----- ADMIN PANEL SECTION -----
@app.route('/admin')
@login_required
@admin_login_required
def home_admin():
    return render_template('admin.html')

@app.route('/admin/create-user', methods=['GET', 'POST'])
@login_required
@admin_login_required
def users_list_admin():
    users = User.query.all()
    return render_template('users-list-admin.html', users=users)

@app.route('/admin/create-user')
@login_required
@admin_login_required
def user_create_admin():    
    form = AdminUserCreateForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        admin = form.admin.data
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username already taken. Try another one.', 'warning')
            return render_template('user-create-admin.html', page_name='Register as admin', form=form)
        
        user = User(username, password, admin) # stage changes
        db.session.add(user) # add staged changes into session
        db.session.commit() # commit session changes
        flash('New user created.', 'success')
        return redirect(url_for('users_list_admin'))
    
    if form.errors:
        flash(form.errors)

    return render_template('user-create-admin.html', page_name='Register as admin', form=form)

@app.route('/admin/update-user/<id>', methods=['GET', 'POST'])
@login_required
@admin_login_required
def user_update_admin(id):
    # Get user or return 404
    user = User.query.get_or_404(id)
    
    # Initialize form with user data
    form = AdminUserUpdateform(obj=user)

    if form.validate_on_submit():
        user.username = form.username.data
        user.admin = form.admin.data
        db.session.commit()
        flash('User updated successfully.', 'success')
        return redirect(url_for('users_list_admin'))
    
    if form.errors:
        flash(form.errors, 'danger')
        
    return render_template('user-update-admin.html', form=form, user=user)

@app.route('/admin/delete-user/<id>', methods=['GET', 'POST'])
@login_required
@admin_login_required
def user_delete_admin(id):
    user = User.query.get(id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted.', 'info')
    return redirect(url_for('users_list_admin'))

'''
Create admin with flask shell
user = User(username='Admin', password='testpassword', admin=True)
db.session.add(user); db.session.commit()
'''
# ----- END OF ADMIN PANEL ROUTING -----

