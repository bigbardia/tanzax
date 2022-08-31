from flask import session , redirect
from tanzax.models import User
from functools import wraps
from datetime import datetime
import pytz


file_extensions = {"py","cpp" ,"pas","pdf","png","jpg","gif","jpeg","jfif" , "zip"}
pic_extensions = {"png" , "jpg","gif","jpeg","jfif"}



def allowed_pic_extension(filename : str) -> bool:
    return "." in filename and filename.rsplit(".",1)[1].lower() in pic_extensions

def allowed_file_extension(filename : str) -> bool:
    return "." in filename and filename.rsplit(".",1)[1].lower() in file_extensions



def login_required(func):
    @wraps(func)
    def wrapper(*args , **kwargs):
        if not is_authenticated():
            logout_user()
            return redirect("/login")
        return func(*args , **kwargs)
    return wrapper


def valid_characters(username : str):
    for i in username:
        if i not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRTUVWXYZ0123456789":
            return False
    return True



def is_aks(file_url : str):
    extension = file_url.split(".")[1]
    if extension in pic_extensions:
        return True
    return False

def to_datetime(timestamp : int):
    dt = datetime.fromtimestamp(timestamp , pytz.timezone("Asia/Tehran"))
    return dt.strftime("%A, %Y-%m-%d %H:%M:%S")


def get_current_user():
    user_id = session.get("user_id")
    return User.query.get(user_id)



def is_authenticated()->bool:
    user_id = session.get("user_id",None)
    user =User.query.get(user_id)
    if not user_id or not user:
        return False
    return True


def login_user(user):
    session.permanent = True
    session["user_id"] = user._id
    
def logout_user():
    session.clear()
    session.permanent = False