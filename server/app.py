# -*- coding: utf-8 -*-



# functions
from flask import g, request, render_template, redirect, url_for
from flask.ext.login import login_user, logout_user

from apiclient.discovery import build

# objects
from flask import Flask
from flask.ext.login import LoginManager

import httplib2
from oauth2client.client import OAuth2WebServerFlow

from models import db, User

# constants
import config



app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)



@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.before_request
def before_request():
    g.auth_flow = OAuth2WebServerFlow(
        client_id = config.GMAIL_CLIENT_ID,
        client_secret = config.GMAIL_CLIENT_SECRET,
        scope = config.GMAIL_AUTH_SCOPE,
        redirect_uri = url_for('login_callback', _external = True)
    )


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
    auth_uri = g.auth_flow.step1_get_authorize_url()
    return redirect(auth_uri)

@app.route('/login/callback/')
def login_callback():
    code = request.args.get('code')
    credentials = g.auth_flow.step2_exchange(code)
    http_auth = credentials.authorize(httplib2.Http())
    api = build('gmail', 'v1', http = http_auth)
    gmail_user = api.users().getProfile(userId = 'me').execute()

    email = gmail_user['emailAddress']
    access_token = credentials.access_token

    user = User.query.filter_by(email = email).first()
    if user:
        user.access_token = access_token

    else:
        user = User(email, access_token)
        db.session.add(user)

    db.session.commit()
    login_user(user, remember = True)

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

