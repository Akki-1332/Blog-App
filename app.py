from datetime import date, datetime
from functools import partial
import re
from flask import Flask,render_template,request, redirect
from flask.globals import session
from flask_mail import Mail, Message
import json
from flask_sqlalchemy import SQLAlchemy
import random as r

with open('config.json', 'r') as c:
    params = json.load(c)['params']
    # m_var = json.load(c)['mail_vars']


app = Flask(__name__)
app.secret_key = 'super secret key'
app.config.update(
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_PORT = "465",
    MAIL_USE_SSL = "True",
    MAIL_USERNAME = params['gmail_username'],
    MAIL_PASSWORD = params['gmail_password']
)
mail = Mail(app)
if params["local_server"] == "True":
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_server_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']

db = SQLAlchemy(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(40), nullable=False)
    phone_num = db.Column(db.String(15), nullable=False)
    msg = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(20), nullable=False)

class Posts(db.Model):
    sn = db.Column(db.Integer, primary_key=True)
    ttl = db.Column(db.String(100), nullable=False)
    tline = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(1000), nullable=False)
    date = db.Column(db.String(20), nullable=False)
    slug = db.Column(db.String(20), nullable=False)
    img_file = db.Column(db.String(20), nullable=False)

@app.route("/")
def home():
    # fetch data from database
    posts = Posts.query.filter_by().all()
    return render_template("index.html", param=params, post=posts)

@app.route("/about")
def about():
    return render_template("about.html", param=params)

@app.route("/post/<string:post_slug>" , methods=['GET', 'POST'])
def post(post_slug):
    post = Posts.query.filter_by(slug=post_slug).first()
    return render_template("post.html", param=params, post=post)

@app.route("/dashboard" , methods=['GET', 'POST'])
def login():
    # It will check if user is already logged in or not
    if ('user' in session and session['user'] == params['admin_user']):
        print("this is logged in ",session)
        posts = Posts.query.filter_by().all()
        return render_template("profile.html", param=params, post=posts)

    # if user isn't logged in then we will login with provided data.
    if request.method == "POST":
        # form data fetching
        my_username = request.form.get("login_name")
        my_password = request.form.get("login_password")

        # form data validation with local database
        if ( my_username == params['admin_user'] ) and ( my_password == params['admin_passwd']):
            # adding session if username and password is correct
            session['user'] = my_username
            print(session)
            posts = Posts.query.filter_by().all()
            return render_template("profile.html", param=params, post=posts)

    return render_template("login.html", param=params)


@app.route("/logout" , methods=['GET', 'POST'])
def logout():
    session.pop("user")
    return render_template("login.html", param=params)



@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # connect to database
        u_name = request.form.get("name")
        u_email = request.form.get("mail")
        u_phone = request.form.get("phn")
        u_message = request.form.get("msg")
        entry = Contacts(name=u_name, email=u_email, phone_num=u_phone, msg=u_message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()  

        # msg = Message(html=)
        
        # otp = r.randint(1000, 9999)

        # mail.send_message("New Message from : " + u_name, 
        #         sender = u_email,
        #         recipients = [params['gmail_username']],
        #         body = "OTP is : \n\n"+ otp +"Varify it."
        #         )

        # u_otp = request.form.get("myotp")
        # if otp == u_otp:
        #     mail.send_message("Thanks for connecting us " + u_name, 
        #             sender = u_email,
        #             recipients = [u_email],
        #             body = render_template("mail.html", my_name=u_name)
        #             )
        

                 
       
    return render_template("contact.html", param=params)

@app.route("/edit/<string:sno>", methods=['GET', 'POST'])
def edit(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if request.method == "POST":
            box_title = request.form.get("title")
            box_tline = request.form.get("tline")
            box_slug = request.form.get("slug")
            box_content = request.form.get("content")
            box_img = request.form.get("img_file")
            date = datetime.now()

            if sno == "0":
                print("new post code")
                # same edit form require
                # database new entry 
                newpost = Posts(ttl=box_title, tline=box_tline, slug=box_slug, content=box_content, img_file=box_img, date=date)   
                db.session.add(newpost)
                db.session.commit()
                return redirect("/dashboard") 
            else:
                # if sno is not 0 then you have to understand that it's about an older post.
                # fetch details of post and change with the given data according to form.
                post = Posts.query.filter_by(sn=sno).first()
                post.ttl = box_title
                post.tline = box_tline
                post.slug = box_slug
                post.content = box_content
                post.img_file = box_img
                post.date = date
                # save the changes to database
                db.session.commit()
                return redirect("/dashboard") 

        if sno == "0":
            zeroPost = {"sn": '0'}
            return render_template("edit.html", param=params, post=zeroPost)
        else:  
            post = Posts.query.filter_by(sn=sno).first()
            return render_template("edit.html", param=params, post=post)
    

@app.route("/delete/<string:sno>", methods=['GET', 'POST'])
def delete(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Posts.query.filter_by(sn=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect("/dashboard")
    


app.run(debug=True)


