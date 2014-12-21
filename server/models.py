# -*- coding: utf-8 -*-



# objects
from flask.ext.login import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy



db = SQLAlchemy()



class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(128), unique = True)

    def __init__(self, email):
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.email

