from flask import Flask, render_template, request, session, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import date
from datetime import datetime
from flask_mail import Mail
import os
import json
from jinja2 import Markup, escape
# from werkzeug import secure_filename
from wtforms import Form, StringField, SelectField

# Reading data from the config.jason file
with open('config.json', 'r') as c:
    params = json.load(c)['params']

local_server = True
app = Flask(__name__)
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER'] = params['upload_locaion']
app.config.update(
    MAIL_SERVER= 'smtp.gmail.com',
    MAIL_PORT= '465',
    MAIL_USE_SSL= True,
    MAIL_USERNAME= params['gmail-user'],
    MAIL_PASSWORD= params['gmail-password']
)
if (local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['production_uri']
db = SQLAlchemy(app)
mail = Mail(app)

class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    email = db.Column(db.String(30), nullable=False)
    msg = db.Column(db.String(50), nullable=False)
    date_time = db.Column(db.String(11))

class Blog(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    tagline = db.Column(db.String(80), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    date_time = db.Column(db.String(20))

class Python(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    tagline = db.Column(db.String(200), nullable=False)
    content = db.Column(db.String(10000), nullable=False)
    slug = db.Column(db.String(30), nullable=False)
    author = db.Column(db.String(20), nullable=False)
    date_time = db.Column(db.String(20))

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if ('user' in session and session['user'] == params['admin_user']):
        return render_template('dashboard.html', params = params)
    if request.method == "POST":
        username = request.form.get('uname')
        userpass = request.form.get('pass')
        #setting the session for the user first date_time
        if (username == params['admin_user'] and userpass == params['admin_password']):
            session['user'] = username
            return render_template('dashboard.html', params = params)
    return render_template('login.html', params = params)

@app.route("/admin/<string:something>", methods=["GET", "POST"])
def admin_edit(something):
    if ('user' in session and session['user'] == params['admin_user']):
        if something == "python":
            posts = Python.query.all()
            return render_template('edit_dashboard.html', posts=posts, params=params, key="python")
        elif something == "blog":
            posts = Blog.query.all()
            return render_template('edit_dashboard.html', posts=posts, params=params, key="blog")
        elif something == "contact":
            contacts = Contacts.query.all()
            return render_template('edit_dashboard.html', contacts=contacts, params=params, key="contacts")
    return render_template('login.html', params = params)

@app.route("/admin/blog/<string:sno>", methods=["GET","POST"])
def edit1(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            content = request.form.get('content')
            slug= request.form.get('slug')
            author = request.form.get('author')

            if sno == "0":
                post = Blog(title=title, tagline=tagline, content=content, slug=slug, author=author, date_time=date.today())
                db.session.add(post)
                db.session.commit()
            else:
                post = blog.query.filter_by(sno=sno).first()
                post.title = title
                post.tagline = tagline
                post.content = content
                post.slug = slug
                post.author = author
                db.session.commit()
                return redirect('/admin/blog/'+ sno)

        post = Blog.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, key="blog")
    return render_template('login.html', params=params)

@app.route("/admin/python/<string:sno>", methods=["GET","POST"])
def edit2(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method == 'POST'):
            title = request.form.get('title')
            tagline = request.form.get('tagline')
            content = request.form.get('content')
            slug= request.form.get('slug')
            author = request.form.get('author')

            if sno == '0':
                post = Python(title=title, tagline=tagline, content=content, slug=slug, author=author, date_time=date.today())
                db.session.add(post)
                db.session.commit()

            else:
                post = Python.query.filter_by(sno=sno).first()
                post.title = title
                post.tagline = tagline
                post.content = content
                post.slug = slug
                post.author = author
                db.session.commit()
                return redirect('/admin/python/'+sno)

        post = Python.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, post=post, key = "python")
    return render_template('login.html', params=params)

@app.route("/admin/contact/<string:sno>", methods=["GET","POST"])
def contact_details(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        contact = Contacts.query.filter_by(sno=sno).first()
        return render_template('edit.html', params=params, contact=contact, key="contact_key")
    return render_template('login.html', params=params)

@app.route("/")
def home():
    posts = Blog.query.filter_by().all()[0:params['number_of_post']]
    return render_template("index.html", params=params, posts=posts,)

@app.route("/blog")
def blog():
    posts = Blog.query.filter_by().all()
    return render_template("blog.html", params=params, posts=posts)

@app.route("/python/<string:post_slug>")
def python(post_slug):
    post = Python.query.filter_by(slug=post_slug).first()
    posts = Python.query.all()
    return render_template('python.html', params=params, posts=posts, post=post)

@app.route("/contact", methods = ["GET", "POST"])
def contact():
    if (request.method == "POST"):
        name = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        message = request.form.get('message')

        entry = Contacts(name=name, phone= phone, email = email, msg= message, date_time= datetime.now())
        db.session.add(entry)
        db.session.commit()
        mail.send_message('New message from ' + name,sender= email, recipients= [params['gmail-user']],body= 'Name: '+ name + '\n'+ 'Email: ' + email + '\n' + 'Phone: ' + phone + '\n' + 'Message: ' + message  )
    return render_template("contact.html", params=params)

@app.route("/blog/<string:post_slug>", methods=["GET"])
def post_page(post_slug):
    post = Blog.query.filter_by(slug=post_slug).first()
    posts = Blog.query.filter_by().all()[0:11]
    return render_template("post.html", params=params, post=post, posts=posts)


@app.route("/admin/python/delete/<string:sno>", methods=["GET","POST"])
def delete_python(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Python.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/admin/python')

@app.route("/admin/blog/delete/<string:sno>", methods=["GET","POST"])
def delete_blog(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Blog.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/admin/blog')

@app.route("/admin/contact/delete/<string:sno>", methods=["GET","POST"])
def delete_contact(sno):
    if ('user' in session and session['user'] == params['admin_user']):
        post = Contacts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
        return redirect('/admin/contact')

@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/admin')

@app.route("/uploader", methods=["GET","POST"])
def uploader():
    if ('user' in session and session['user'] == params['admin_user']):
        if (request.method=="POST"):
            f = request.files['file_upload']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded Successfully"
    return render_template('login.html', params = params)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


app.run(debug=True)
