import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__)) # get absolute path of the current file
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')  # secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'products.db') # locate products database
db = SQLAlchemy(app) # initalise db
migrate = Migrate(app, db) # initalise migrate

ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif']) # allow what extentions to be uploaded
app.config['UPLOAD_FOLDER'] = os.path.realpath('.') + '/app/static/images' # tell flask where to put images

# Flask-Login initialisation
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from app import routes # get routes or endpoints

with app.app_context():
    db.create_all()