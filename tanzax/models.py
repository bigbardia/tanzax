from tanzax.ext import db
from time import time
from passlib.hash import bcrypt


def int_time():
    return int(time())

class User(db.Model):

    __tablename__ = "users"

    _id = db.Column(db.Integer , primary_key = True)
    username = db.Column(db.String(50), nullable = False)
    hashed_password = db.Column(db.String(50) , nullable = False)
    timestamp = db.Column(db.Integer, default=int_time , nullable = False)
    bio = db.Column(db.Text , nullable = True)
    image_url = db.Column(db.String(100), nullable = True , default = "/media/default.jpeg")
    last_ping = db.Column(db.Integer , nullable = True , default = int_time)
    posts = db.relationship("Post",backref = "author")
    comments = db.relationship("Comment" , backref = "commenter")
    likes = db.relationship("Like" , backref = "liker")

    def __init__(self , username , password , bio="" , image_url="/media/default.jpeg"):
        self.username = username
        self.hashed_password = self.hash_password(password)        
        self.bio = bio
        self.image_url = image_url
    
    def __repr__(self):
        return f"<User {self.username}>"

    @property
    def get_profile_url(self):
        return f"/profile/{self.username}"

    def hash_password(self,password):
        return bcrypt.hash(password)
    
    def verify_password(self , password) -> bool:
        return bcrypt.verify(password , self.hashed_password)


class Post(db.Model):

    __tablename__ = "posts"

    _id = db.Column(db.Integer, primary_key = True )
    title = db.Column(db.String(32), nullable = False)
    text = db.Column(db.String(512), nullable = True )
    file_url = db.Column(db.String(512) , nullable = True)
    author_id = db.Column(db.Integer,db.ForeignKey("users._id") , nullable = False)
    timestamp = db.Column(db.Integer , default = int_time , nullable = False)
    comments = db.relationship("Comment" , backref = "post")
    likes = db.relationship("Like" , backref = "post" )
    like_counter = db.Column(db.Integer , default = 0 , nullable = False)

    @property
    def get_post_url(self):
        return f"/posts/{self._id}"


    def __init__(self , title , text=None , file_url = None):
        self.title = title
        self.text = text
        self.file_url = file_url

    def __repr__(self):
        return f"<Post {self.title}>"

class Comment(db.Model):

    __tablename__ = "comments"

    _id = db.Column(db.Integer , primary_key = True)
    text = db.Column(db.String(256) , nullable = False)
    post_id = db.Column(db.Integer, db.ForeignKey("posts._id") , nullable = False)
    commenter_id = db.Column(db.Integer , db.ForeignKey("users._id") , nullable = False)
    timestamp = db.Column(db.Integer , default = int_time , nullable = False)

    def __repr__(self):
        return f"<Comment {self.commenter , self.post}>"

    def __init__(self , text , post , commenter):
        self.text =text
        self.post = post
        self.commenter = commenter

class Like(db.Model):
    
    __tablename__ = "likes"
    _id = db.Column(db.Integer , primary_key = True)
    timestamp = db.Column(db.Integer , default = int_time , nullable = False)
    post_id = db.Column(db.Integer , db.ForeignKey("posts._id") , nullable = False)
    liker_id = db.Column(db.Integer , db.ForeignKey("users._id") , nullable = False)
    
    def __init__(self, post , liker):
        self.post = post
        self.liker = liker

    def __repr__(self):
        return f"<Like {self.liker} , {self.post}>"
