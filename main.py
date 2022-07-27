from functools import wraps
from pydoc import plain
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session,
    url_for,
)
from flask_wtf import CSRFProtect
import uuid
import os
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from dotenv import load_dotenv
from time import time
from xss import escape_javascript


load_dotenv()

app = Flask(__name__ ,template_folder="templates",static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.sqlite3"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config["PERMANENT_SESSION_LIFETIME"] = 60 * 60 * 24 * 14 #2 weeks
db = SQLAlchemy(app = app)
csrf = CSRFProtect(app=app)



#-----
def login_required(func):
    @wraps(func)
    def wrapper(*args , **kwargs):
        user_id = session.get("user_id", None)
        user = User.query.get(user_id)
        if not user_id or not user:
            session.clear()
            session.permanent = False
            return redirect("/login")
        return func(*args , **kwargs)
    return wrapper


def login_user(user):
    session.permanent = True
    session["user_id"] = user._id
    
def logout_user():
    session.clear()
    session.permanent = False

def int_time():
    return int(time())


def get_current_user():
    user_id = session.get("user_id")
    return User.query.get(user_id)


#-----------------------------------------------------------
#MODELS


class User(db.Model):

    __tablename__ = "users"

    _id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(50), nullable = False)
    hashed_password = db.Column(db.String(50) , nullable = False)
    timestamp = db.Column(db.Integer, default=int_time , nullable = False)
    bio = db.Column(db.Text , nullable = True)


    def __init__(self , username , password , bio=None):
        self.username = username
        self.hashed_password = self.hash_password(password)        
        self.bio = bio
    
    def __repr__(self):
        return f"<User {self.username}>"

    def hash_password(self,password):
        return bcrypt.hash(password)
    
    def verify_password(self , password) -> bool:
        return bcrypt.verify(password , self.hashed_password)


#----------------
#ROUTES


@app.route("/signup" , methods = ["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        errors = []

        if not username:
            errors.append("اقای محرتم!!!!!یوزرنیم لازم میباشد")
        
        elif User.query.filter_by(username = username).first():
            errors.append("یوزرنیم الردی در پایاگاه دیتا وجود دارد")

        if not password:
            errors.append("پسسورد الزمامیست۱")
        elif len(password) < 8:
            errors.append("رمز عبور شما از کوتاهی رنج می برد")
        
        if len(errors) != 0:
            for error in errors:
                flash(error)
            return redirect("/signup")
    
        user = User(username, password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect("/")
    
@app.route("/login" , methods = ["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":

        username = request.form.get("username" , None)
        password = request.form.get("password" , None)
        user : User = User.query.filter_by(username = username).first()
        if not user:
            flash("یوزر وجود ندارد")
            return redirect("login")
        
        if not user.verify_password(password):
            flash("پسسورد غلط است")
            return redirect("/login")

        login_user(user)
        return redirect("/")


@app.route("/profile" , methods = ["GET","POST"])
@login_required
def edit_profile():

    if request.method == "GET":
        return render_template("profile.html")

    elif request.method == "POST":
        user = get_current_user()
        plain_text = request.form.get("plain_text" , None)
        plain_text = escape_javascript(plain_text)
        user.bio = plain_text
        db.session.commit()
        return redirect("/profile")

@app.route("/profile/<_id>")
def profile_view(_id):
    if request.method == "GET":
        user = User.query.get_or_404(_id)
        context = {}
        if request.args.get("html",None):
            context["html"] = True
            context["bio"] = user.bio
            return render_template("profile_view.html",**context)

        context["bio_url"] = url_for("profile_view",_id = _id) +"?html=true"
        context["username"]= user.username
        context["timestamp"] = user.timestamp
        return render_template("profile_view.html" , **context)

@app.route("/logout")
def logout():
    logout_user()
    return redirect("/login")

@app.route("/test")
def test():
    return f"{session.items()}"


@app.route("/")
@login_required
def index():
    return render_template("index.html")


if __name__ == "__main__":
    db.create_all()
    app.run(debug = True , threaded = True)
