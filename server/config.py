# -*- coding: utf-8 -*-



# builtins
import os
import uuid


# for session to be usable
SECRET_KEY = uuid.uuid4().hex

# location of DB
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

# Gmail OAuth info
GMAIL_CLIENT_ID = os.environ['GMAIL_CLIENT_ID']
GMAIL_CLIENT_SECRET = os.environ['GMAIL_CLIENT_SECRET']
GMAIL_AUTH_SCOPE = 'https://www.googleapis.com/auth/gmail.readonly'

# Useful in production, for logging
PROPAGATE_EXCEPTIONS = True

