from flask import Flask
from tanzax.ext import csrf , db
import os
from dotenv import load_dotenv
from tanzax.main import views
from tanzax.utils import *

load_dotenv()

def create_app():

    app = Flask(__name__)

    app = Flask(__name__ ,template_folder="templates",static_folder="static")
    app.secret_key = "8952f5ca7c1244f0b6f9e4090cacd12a"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:////var/www/html/tanzax/user.sqlite3"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
    app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 14 #2 weeks
    app.config["SESSION_COOKIE_HTTPONLY"] = False
    app.config["UPLOAD_FOLDER"] = "/var/www/html/tanzax/tanzax/uploads"
    app.config['MAX_CONTENT_LENGTH'] = 20 * 1000 * 1000 # 20 megabytes

    app.register_blueprint(views)

    csrf.init_app(app)
    db.init_app(app)

    with app.app_context():
        db.create_all()


    app.jinja_env.globals.update(to_datetime = to_datetime)
    app.jinja_env.globals.update(is_aks = is_aks)
    app.jinja_env.globals.update(current_user = get_current_user)
    app.jinja_env.globals.update(is_authenticated = is_authenticated)

    return app
