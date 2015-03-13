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
from wtforms import SubmitField, SelectMultipleField
from wtforms.validators import DataRequired, Email
from wtforms.widgets import CheckboxInput, ListWidget

from models import db, User, Bookmark

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
        if request.endpoint == 'bookmarks':
            return redirect(url_for('home'))

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


class AddBookmarkForm(Form):
    bookmark = EmailField('New Bookmark', validators = [DataRequired(), Email()])
    submit = SubmitField('Add')

    def validate(self):
        is_valid = super(AddBookmarkForm, self).validate()
        if not is_valid:
            return False

        bookmark = current_user.bookmarks.filter_by(email = self.bookmark.data).first()
        if bookmark:
            self.bookmark.errors.append(u'Already registered.')
            return False

        return True

class RemoveBookmarkForm(Form):
    bookmarks = SelectMultipleField('Remove Bookmarks', option_widget = CheckboxInput(), widget = ListWidget(prefix_label = False))
    submit = SubmitField('Remove')

    def __init__(self, *args, **kwargs):
        super(RemoveBookmarkForm, self).__init__(*args, **kwargs)

        bookmarks = current_user.bookmarks.order_by('email')
        choices = [bookmark.email for bookmark in bookmarks]
        self.bookmarks.choices = zip(choices, choices)

    def validate(self):
        is_valid = super(RemoveBookmarkForm, self).validate()
        if not is_valid:
            return False

        if not self.bookmarks.data:
            self.bookmarks.errors.append(u'Nothing selected.')
            return False

        return True

@app.route('/bookmarks/', methods = ['GET', 'POST'])
def bookmarks():
    form_add = AddBookmarkForm()
    form_remove = RemoveBookmarkForm()

    action = request.form.get('submit', '').lower()

    if action == 'add':
        if form_add.validate_on_submit():
            bookmark = Bookmark(current_user, form_add.bookmark.data)
            db.session.add(bookmark)
            db.session.commit()
            flash('Saved.', 'success')

            return redirect(url_for('bookmarks'))

    elif action == 'remove':
        if form_remove.validate_on_submit():
            for email in form_remove.bookmarks.data:
                bookmark = current_user.bookmarks.filter_by(email = email).first()
                db.session.delete(bookmark)

            db.session.commit()
            flash('Removed.', 'success')

            return redirect(url_for('bookmarks'))

    return render_template('bookmarks.html', form_add = form_add, form_remove = form_remove)


@app.route('/keep-alive')
def keep_alive():
    return 'OK'


@app.route('/')
def home():
    return render_template('home.html')



# dev server
if __name__ == '__main__':
    app.run(debug = True)

