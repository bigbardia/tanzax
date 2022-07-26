from flask import (
    Flask,
    request
)
import os
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import bcrypt
from dotenv import load_dotenv


load_dotenv()



app = Flask(__name__ ,template_folder="templates",static_folder="static")
app.secret_key = os.environ.get("SECRET_KEY")
app.config[""]
db = SQLAlchemy(app = app)

#-----------------------------------------------------------
#MODELS


class User(db.Model):
    _id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(50), nullable = False)
    hashed_password = db.Column(db.String(50) , nullable = False)

    def __init__(self , username , password):
        self.username = username
        self.hashed_password = self.hash_password(password)        
    
    def __repr__(self):
        return f"<User {self.username}>"

    def hash_password(self,password):
        return bcrypt.hash(password)
    
    def verify_password(self , password) -> bool:
        return bcrypt.verify(password , self.hashed_password)



#----------------
#ROUTES

def signup():
    pass



if __name__ == "__main__":
    app.run(debug = True , threaded = True)