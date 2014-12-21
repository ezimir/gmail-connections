# -*- coding: utf-8 -*-



# functions
from flask import g, request, render_template, redirect, url_for, flash
from flask.ext.login import login_user, logout_user, current_user

from apiclient.discovery import build

# objects
from flask import Flask
from flask.ext.login import LoginManager

import httplib2
from oauth2client.client import OAuth2WebServerFlow, AccessTokenCredentials

from flask_wtf import Form
from flask_wtf.html5 import EmailField
from wtforms import SubmitField
from wtforms.validators import DataRequired, Email

from models import db, User

# constants
import config



app = Flask(__name__)
app.config.from_pyfile('config.py')

db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)



def get_api(credentials):
    http_auth = credentials.authorize(httplib2.Http())
    return build('gmail', 'v1', http = http_auth)



@login_manager.user_loader
def load_user(userid):
    return User.query.get(int(userid))

@app.before_request
def before_request():
    if not current_user.is_authenticated():
        g.auth_flow = OAuth2WebServerFlow(
            client_id = config.GMAIL_CLIENT_ID,
            client_secret = config.GMAIL_CLIENT_SECRET,
            scope = config.GMAIL_AUTH_SCOPE,
            redirect_uri = url_for('login_callback', _external = True)
        )

    else:
        credentials = AccessTokenCredentials(current_user.access_token, u'')
        g.gmail_api = get_api(credentials)


@app.context_processor
def inject_menu():
    return {
        'menu': [
            ('home', 'Home'),
            ('bookmarks', 'Bookmarks'),
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
    gmail_api = get_api(credentials)
    gmail_user = gmail_api.users().getProfile(userId = 'me').execute()

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


class BookmarkForm(Form):
    bookmark = EmailField('New Bookmark', validators = [DataRequired(), Email()])
    submit = SubmitField('Add')

@app.route('/bookmarks/', methods = ['GET', 'POST'])
def bookmarks():
    form = BookmarkForm()
    if form.validate_on_submit():
        flash('Saved.', 'success')
        return redirect(url_for('bookmarks'))

    return render_template('bookmarks.html', form = form)


@app.route('/')
def home():
    return render_template('home.html')



# dev server
if __name__ == '__main__':
    app.run(debug = True)

