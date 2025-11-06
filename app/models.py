from app import db
from wtforms import StringField, DecimalField, SelectField, FileField, ValidationError, PasswordField, BooleanField
from wtforms.validators import NumberRange, EqualTo, InputRequired
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from decimal import Decimal
from app import db

# custom validators 
def check_duplicate_categories(case_sensitive=True):
    def check_duplicate(form, field):
        if case_sensitive:
            category_query = Category.query.filter(Category.name.like('%' + field.data + '%')).first() # check if category exists
        else:
            category_query = Category.query.filter(Category.name.ilike('%' + field.data + '%')).first()
        if category_query:
            raise ValidationError(f'Category {field.data} exists already.')
    return check_duplicate


# forms
class NameForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired()]) # requires user to input

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[InputRequired(), check_duplicate_categories()]) # requires user to input and must not be duplicate category name

class ProductForm(NameForm):
    price = DecimalField('Product Price', validators=[InputRequired(), NumberRange(min=Decimal('0.01'))]) # allow numbers minimum of 0.01
    category = SelectField('Category', validators=[InputRequired()], coerce=int) # requires input
    image = FileField('Product image', validators=[FileRequired()]) # requires image

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()]) # requires input
    password = PasswordField('Password', [InputRequired(), EqualTo('confirm', message='Passwords must match')]) # requires input and input must match 'confirm' variable
    confirm = PasswordField('Confirm Password', validators=[InputRequired()]) # requires input

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()]) # requires input
    password = PasswordField('Password', validators=[InputRequired()]) # requires input

class AdminUserCreateForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    admin = BooleanField('Make user admin?')

class AdminUserUpdateform(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    admin = BooleanField('Make user admin?')

# databases
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True) # make id the primary key
    name = db.Column(db.String(255), nullable=False) # max input of 255 characters, must contain something
    price = db.Column(db.Float, nullable=False) # allow decimal numbers, must contain something
    image_path = db.Column(db.String(255), nullable=False) # max input of 255 characters, must contain something
    category_id = db.Column(db.Integer, db.ForeignKey('category.id')) # foreign key link to category table
    category = db.relationship('Category', backref=db.backref('products', lazy='dynamic')) # establish relationship with category table

    def __init__(self, name, price, category, image_path):
        self.name = name
        self.price = price
        self.category = category
        self.image_path = image_path
        

    def __repr__(self):
        return '<Product %d>' % self.id
    
class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True) # make id the primary key
    name = db.Column(db.String(100), nullable=False) # max input of 100 characters, must contain something

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %d>' % self.id

# user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # make id the primary key
    username = db.Column(db.String(100), nullable=False) # max 100 characters, must contain something
    password_hash = db.Column(db.String()) # string only
    admin = db.Column(db.Boolean()) # Boolean only (True and false)

    @property
    def is_authenticated(self):
        return True
    @property
    def is_active(self):
        return True
    @property
    def is_anonymous(self):
        return False
    def get_id(self):
        return str(self.id)
    
    def __init__(self, username, password, admin):
        self.username = username
        self.password_hash = generate_password_hash(password)
        self.admin = admin

    def is_admin(self):
        return self.admin

    def check_password(self, password):
        return check_password_hash(self.password_hash, password) # check if password match
    
class Cart(db.Model):
    id = db.Column(db.Integer, primary_key=True) # make id the primary key
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    user = db.relationship('User', backref=db.backref('cart', lazy='select')) # create relationship with User and back to Cart again
    items = db.relationship('CartItem', backref=db.backref('cart', lazy='select'), cascade='all, delete-orphan', lazy='select') # new parameter cascade. It is useful as when we delete the Cart database table, all of CartItems will also be removed too.
    # difference of lazy loading includes dynamic and select, basically dynamic gives a query object whereas select is the default on demand data obtainment

    def __init__(self, user_id):
        self.user_id = user_id

    def add_item(self, product, quantity=1):
        cart_item = CartItem.query.filter_by(cart_id=self.id, product_id=product.id).first()
        if cart_item: # checks if item is a duplicate or not. If it is, just add the item by 1
            cart_item.quantity += quantity
        else:
            cart_item = CartItem(self.id, product.id, quantity) # if not it is a new item so commit the item into database as new entry
            db.session.add(cart_item)

    def remove_item(self, product, quantity=1):
        cart_item = CartItem.query.filter_by(cart_id=self.id, product_id=product.id).first()
        if cart_item:
            if (cart_item - quantity) > 1:
                cart_item.quantity -= quantity
            else:
                cart_item.delete()
        return cart_item
    
    def get_items(self):
        items_list = []
        for cart_item in self.items:
            items_list.append({
                'product': cart_item.product,
                'quantity': cart_item.quantity,
                'subtotal': cart_item.subtotal
            })
        return items_list

    @property
    def total(self):
        total = Decimal('0.00')
        for item in self.items:
            total += item.subtotal
        return total

        
            
    
class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cart_id = db.Column(db.Integer, db.ForeignKey('cart.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)

    product = db.relationship('Product') 
    # create relationship with Product model. Will need to use later to refer to this database for price of items
    # no need back reference because product would not need to access cartitem model anyways.

    def __init__(self, cart_id, product_id, quantity):
        self.cart_id = cart_id
        self.product_id = product_id
        self.quantity = quantity

    @property
    def subtotal(self):
        price = getattr(self.product, 'price', None)
        if price is None:
            return Decimal('0.00')
        else:
            return Decimal(str(price)) * Decimal(self.quantity)

