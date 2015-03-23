# -*- coding: utf-8 -*-



# objects
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy



db = SQLAlchemy()



class User(UserMixin, db.Model):

    __tablename__ = 'gc-users'

    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(128), unique = True)
    access_token = db.Column(db.String(255))
    bookmarks = db.relationship('Bookmark', backref = 'bookmark', lazy = 'dynamic')

    def __init__(self, email, access_token):
        self.email = email
        self.access_token = access_token

    def __repr__(self):
        return u'<User {}>'.format(self.email)


class Bookmark(db.Model):

    __tablename__ = 'gc-bookmarks'

    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('{}.id'.format(User.__tablename__)))
    email = db.Column(db.String(128))

    def __init__(self, user, email):
        self.user_id = user.id
        self.email = email

    def __repr__(self):
        return u'<Bookmark {} for #{}>'.format(self.email, self.user_id)

