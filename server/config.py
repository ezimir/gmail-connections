# -*- coding: utf-8 -*-



# builtins
import os
import uuid


# for session to be usable
SECRET_KEY = uuid.uuid4().hex

# location of DB
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

