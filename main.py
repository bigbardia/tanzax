from functools import wraps
from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    session
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
        if not user_id:
            return redirect("/signup")
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
def edit_profile():
    if request.method == "GET":
        return render_template("profile.html")

    elif request.method == "POST":
        plain_text = request.form.get("plain_text" , None)

        return redirect("/profile")




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
    return "Hello"


if __name__ == "__main__":
    db.create_all()
    app.run(debug = True , threaded = True)

