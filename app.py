import sqlite3
from flask import Flask, render_template, session, url_for, redirect, request, flash, g
app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')

app.secret_key = "b'\x1a\xe3$e=(\xdc$\xf6\x95}\x00z\x1c\xae\xc2\n\x1a\x08\x85\x1f#9M\xff\xef=x\rg\x9c\xc9'"
DATABASE = './assignment3.db'

##TODO: Check if username AND password in the session correlate with a user in the database then display pages iff that is the case
##TODO: Check whether username and password that is sent by POST request matches one in the database only then add them to the session and redirect them to the home screen

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

##LOGIN/SIGNUP REQUESTS
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        ##If doesnt equal a username and password combination then return an error message
        if request.form['username'] != 'admin' or request.form['password'] != 'thesecretestsecretpassword':
            error = 'Invalid credentials'
        else:
            session['username'] = request.form['username']
            session['password'] = request.form['password']
            return render_template("index.html")
    return render_template('login.html', error=error)

##LOGOUT REQUESTS
@app.route('/logout')
def logout():
   ## Removes the username and password from the session if it exists
   session.pop('username', None)
   session.pop('password', None)
   return redirect(url_for('login'))
    
if __name__ == "__main__":
    app.run(debug=True)