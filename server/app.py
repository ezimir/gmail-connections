# -*- coding: utf-8 -*-



# functions
from flask import render_template, redirect, url_for
from flask.ext.login import login_user, logout_user, current_user

# objects
from flask import Flask
from flask.ext.login import LoginManager

from models import db, User



app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)




@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))



@app.context_processor
def inject_user():

    return {
        'user': current_user,
    }

@app.context_processor
def inject_menu():
    return {
        'menu': [
            ('home', 'Home'),
            ('home', 'Bookmarks'),
            ('home', 'View Data'),
            ('logout', 'Logout'),
        ],
    }



@app.route('/login/')
def login():
    user = load_user(1)
    login_user(user)
    return redirect(url_for('home'))

@app.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('home.html')



# dev server
if __name__ == '__main__':
    app.run(debug = True)

