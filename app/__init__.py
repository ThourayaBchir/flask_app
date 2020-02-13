from flask import Flask
from config import Config
from .database import mongo
from flask_login import LoginManager
from flask_bootstrap import Bootstrap


app = Flask(__name__)
Bootstrap(app)
app.config.from_object(Config)
mongo.init_app(app)
login = LoginManager(app)
login.login_view = 'login'
from app import views
