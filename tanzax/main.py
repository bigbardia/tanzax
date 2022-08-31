from flask import (
    Blueprint,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    send_from_directory,
    abort,
    current_app
)
import uuid
import os
from tanzax.xss import escape_javascript
from tanzax import db
from tanzax.models import  *
from tanzax.utils import *




views = Blueprint("views" , __name__ , template_folder="templates" , static_folder="static" )



@views.route("/signup" , methods = ["GET","POST"])
def signup():
    if request.method == "GET":
        return render_template("signup.html")
    elif request.method == "POST":
        username = request.form.get("username", None)
        password = request.form.get("password", None)
        errors = []

        if not username:
            errors.append("اقای محرتم!!!!!یوزرنیم لازم میباشد")
        
        
        elif not valid_characters(username):
            errors.append("از کاراکتر های اشتباه استفاده کردید")
        
        elif User.query.filter_by(username = username).first():
            errors.append("یوزرنیم وجود دارد")
        

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
    
@views.route("/login" , methods = ["GET","POST"])
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


@views.route("/profile/<username>")
def profile_view(username):
    if request.method == "GET":
        user = User.query.filter_by(username = username).first()
        if not user:
            abort(404)
        context = {"user" : user}
        if request.args.get("html",None):
            context["html"] = True
            return render_template("profile_view.html",**context)
        
        context["online"] = False
        current_time = int_time()
        if current_time - user.last_ping  <  20:
            context["online"] = True

        context["bio_url"] = url_for("views.profile_view",username = username) +"?html=true"
        return render_template("profile_view.html" , **context)

@views.route("/logout")
def logout():
    logout_user()
    return redirect("/login")


@views.route("/profile" , methods = ["GET","POST"])
@login_required
def edit_profile():

    if request.method == "GET":
        return render_template("profile.html" , user = get_current_user())

    elif request.method == "POST":

        user = get_current_user()
        plain_text = request.form.get("plain_text" , None)
        image_url = user.image_url
        file = request.files.get("pic" , None)
        if plain_text:
            plain_text = escape_javascript(plain_text)
        if file:
            if not allowed_pic_extension(file.filename):
                flash("پسوند فیل قابل قبول نیست")
                return redirect("/profile")
            file.filename = uuid.uuid4().hex + "." + file.filename.rsplit(".",1)[1]
            file.save(os.path.join(current_app.config["UPLOAD_FOLDER"],file.filename))    #CHANGED HERE
            image_url = f"/media/{file.filename}"


        user.bio = plain_text
        user.image_url = image_url
        db.session.commit()
        return redirect("/profile")


@views.route("/ping")
def ping():
    user = get_current_user()
    user.last_ping = int_time()
    db.session.commit()
    return {"message" : "success"}


@views.route('/media/<name>')
def view_file(name):
    return send_from_directory("uploads", name)



@views.route("/" , methods = ["GET","POST"])
@login_required
def index():
    if request.method == "GET":
        context = {}
        sort_by = request.args.get("sort_by",None)
        if sort_by:
            if sort_by == "new":
                context["posts"] = Post.query.order_by(Post.timestamp.desc())
                return render_template("index.html" , **context)
            elif sort_by == "like":
                context["posts"] = Post.query.order_by(Post.like_counter.desc())
                return render_template("index.html" , **context)
        context["posts"] = Post.query.order_by(Post.timestamp.desc())
        return render_template("index.html" , **context)

    elif request.method == "POST":
        if request.form.get("submit_comment" , None):
            comment_text = request.form.get("comment_text")
            errors_msgs = []
            if not comment_text:
                errors_msgs.append("کامنت خالی قبول نیست")
            elif comment_text.count(" ") == len(comment_text):
                errors_msgs.append("خالی قبول نیست")
            elif len(comment_text) > 256:
                errors_msgs.append("گندس")

            if len(errors_msgs) > 0:
                for error in errors_msgs:
                    flash(error)
                return redirect("/")

            post_id = request.form.get("post_id",None)
            post = Post.query.get(post_id)
            comment = Comment(comment_text , post , get_current_user())
            db.session.add(comment)
            db.session.commit()
            return redirect(post.get_post_url)

        else:
            user = get_current_user()
            title = request.form.get("title" , None)
            text = request.form.get("text" , None)
            file = request.files.get("file",None)

            error_msgs = []

            if not title:
                error_msgs.append("تایتل الزامیست")
            elif len(title) > 32:
                error_msgs.append("تایتل گندس")
            elif title.count(" ") == len(title):
                error_msgs.append("تایتل رو خالی نده")

            if not file and not text:
                error_msgs.append("فایل یا متن الزامیست")

            if text:
                if len(text) > 512:
                    error_msgs.append("گندس")
                elif text.count(" ") == len(text):
                    error_msgs.append('متن رو خالی نده')


            file_url = None
            
            if file:
                if not allowed_file_extension(file.filename):
                    error_msgs.append("فایل درست نیست")
                if len(error_msgs) == 0:
                    file.filename = uuid.uuid4().hex + "." + file.filename.rsplit(".",1)[1]
                    file.save(os.path.join(current_app.config["UPLOAD_FOLDER"], file.filename)) #CHANGED HEE
                    file_url = f"/media/{file.filename}"

            if len(error_msgs) > 0:
                for error in error_msgs:
                    flash(error)    
                return redirect("/")
                
            post = Post(title , text , file_url)
            post.author = user
            db.session.add(post)
            db.session.commit()
            return redirect("/")

@views.route("/like_posts" , methods = ["POST"])
@login_required
def like_post():
    request_xhr_key = request.headers.get("X-Requested-With" , None)
    if request_xhr_key and request_xhr_key == "XMLHttpRequest":
        user = get_current_user()
        post_id = int(request.form.get("post_id"))
        post = Post.query.get(post_id)
        like = Like.query.filter_by(liker_id = user._id , post_id = post_id).first()
        if like:
            post.likes.remove(like)
            post.like_counter -= 1
            db.session.delete(like)
        else:
            post.likes.append(Like(post , user))
            post.like_counter += 1
        db.session.commit()
        likes = post.likes.__len__()
        return {"likes" : likes}
    abort(404)


@views.route("/posts/<_id>" , methods = ["GET","POST"]) 
def view_post(_id):
    if request.method == "GET":
        context = {
        "post" : Post.query.get_or_404(_id),
        "comments" : Comment.query.filter_by(post_id = _id).order_by(Comment.timestamp.desc())
        }
        return render_template("post.html" , **context)

    elif request.method == "POST":

        
        comment_text = request.form.get("comment_text")
        errors_msgs = []
        post_id = request.form.get("post_id",None)
        post = Post.query.get(post_id)
        if not comment_text:
            errors_msgs.append("کامنت خالی قبول نیست")
        elif comment_text.count(" ") == len(comment_text):
            errors_msgs.append("خالی قبول نیست")
        elif len(comment_text) > 256:
            errors_msgs.append("گندس")

        if len(errors_msgs) > 0:
            for error in errors_msgs:
                flash(error)
            return redirect(post.get_post_url)

        
        comment = Comment(comment_text , post , get_current_user())
        db.session.add(comment)
        db.session.commit()
        return redirect(post.get_post_url)



@views.app_errorhandler (404)
def page_not_found (e):
    return render_template("404.html"), 404

