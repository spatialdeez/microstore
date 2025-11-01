from app import db
from wtforms import StringField, DecimalField, SelectField, FileField, ValidationError
from wtforms.validators import input_required, NumberRange
from flask_wtf.file import FileRequired
from flask_wtf import FlaskForm
from decimal import Decimal

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
    name = StringField('Name', validators=[input_required()]) # requires user to input

class CategoryForm(FlaskForm):
    name = StringField('Name', validators=[input_required(), check_duplicate_categories()]) # requires user to input and must not be duplicate category name

class ProductForm(NameForm):
    price = DecimalField('Product Price', validators=[input_required(), NumberRange(min=Decimal('0.01'))]) # allow numbers minimum of 0.01
    category = SelectField('Category', validators=[input_required()], coerce=int)
    image = FileField('Product image', validators=[FileRequired()])


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
    name = db.Column(db.String(100)) # max imput of 100 characters

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %d>' % self.id
