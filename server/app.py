# -*- coding: utf-8 -*-



# functions
from flask import render_template

# objects
from flask import Flask



app = Flask(__name__)



@app.context_processor
def inject_user():
    return {
        'user': None,
    }

@app.context_processor
def inject_menu():
    return {
        'menu': [
            ('home', 'Home'),
            ('home', 'Bookmarks'),
            ('home', 'View Data'),
            ('home', 'Logout'),
        ],
    }


@app.route('/')
def home():
    return render_template('home.html')


# dev server
if __name__ == '__main__':
    app.run(debug = True)

