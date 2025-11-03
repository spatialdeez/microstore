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
    name = db.Column(db.String(255)) # max imput of 255 characters
    price = db.Column(db.Float) # allow decimal numbers
    image_path = db.Column(db.String(255)) # max input of 255 characters
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
    name = db.Column(db.String(100)) # max input of 100 characters

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %d>' % self.id

# user model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # make id the primary key
    username = db.Column(db.String(100)) # max 100 characters
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

