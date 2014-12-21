# -*- coding: utf-8 -*-



# objects
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy



db = SQLAlchemy()



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(128), unique = True)
    access_token = db.Column(db.String(255))

    def __init__(self, email, access_token):
        self.email = email
        self.access_token = access_token

    def __repr__(self):
        return '<User %r>' % self.email

