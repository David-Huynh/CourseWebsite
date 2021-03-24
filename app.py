import sqlite3
from flask import Flask, render_template, session, url_for, redirect, request, flash, g
app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')

app.secret_key = "b'\x1a\xe3$e=(\xdc$\xf6\x95}\x00z\x1c\xae\xc2\n\x1a\x08\x85\x1f#9M\xff\xef=x\rg\x9c\xc9'"
DATABASE = './assignment3.db'

##DATABASE CONNECTION
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

##SESSION SETTINGS
@app.before_request
def before_request():
    session.permanent = True

##WEB APP ROUTES
@app.route('/')
def home():
    if 'username' in session:
        return render_template("index.html")
    return redirect(url_for('login'))
@app.route('/lectures')
def lectures():
    if 'username' in session:
        return render_template("lectures.html")
    return redirect(url_for('login'))

@app.route('/coursework')
def coursework():
    if 'username' in session:
        return render_template("courseWork.html")
    return redirect(url_for('login'))

@app.route('/links')
def links():
    if 'username' in session:
        return render_template("links.html")
    return redirect(url_for('login'))

##LOGIN/LOGOUT/SIGNUP REQUESTS
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST': 
        if request.form['username'] != 'admin' or request.form['password'] != 'thesecretestsecretpassword':
            error = 'Invalid credentials'
        else:
            session['username'] = request.form['username']
            return render_template("index.html")
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    error = None
    if request.method == 'POST': 
        if request.form['username'] != 'admin' or request.form['password'] != 'thesecretestsecretpassword':
            error = 'Invalid credentials'
        else:
            session['username'] = request.form['username']
            return render_template("index.html")
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
   # remove the username from the session if it is there
   session.pop('username', None)
   return redirect(url_for('home'))
    
if __name__ == "__main__":
    app.run(debug=True)