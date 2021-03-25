import sqlite3
from flask import Flask, render_template, session, url_for, redirect, request, flash, g
app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')

app.secret_key = "b'\x1a\xe3$e=(\xdc$\xf6\x95}\x00z\x1c\xae\xc2\n\x1a\x08\x85\x1f#9M\xff\xef=x\rg\x9c\xc9'"
DATABASE = './assignment3.db'



##DATABASE CONNECTION AND QUERY
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = make_dicts
    return db
def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def insert_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()

##SESSION SETTINGS
@app.before_request
def before_request():
    session.permanent = True
## ON APPLICATION CLOSE
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
##WEB APP ROUTES
@app.route('/')
def home():
    if 'username' in session and 'password' in session:
        return render_template("index.html")
    return redirect(url_for('login'))
@app.route('/lectures')
def lectures():
    if 'username' in session and 'password' in session:
        return render_template("lectures.html")
    return redirect(url_for('login'))

@app.route('/coursework')
def coursework():
    if 'username' in session and 'password' in session:
        return render_template("courseWork.html")
    return redirect(url_for('login'))

@app.route('/links')
def links():
    if 'username' in session and 'password' in session:
        return render_template("links.html")
    return redirect(url_for('login'))

##LOGIN/SIGNUP REQUESTS
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['firstname'] == '' and request.form['lastname'] == '':
            ##Queries whether there is a username and password match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code,password FROM instructor WHERE (instructor_code=\"" + 
            request.form['username'] + "\" AND password=\"" + request.form['password'] + "\")) AS \"col\"")
            ##Queries whether there is a username and password match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=\"" + 
            request.form['username'] + "\" AND password=\"" + request.form['password'] + "\")) AS \"col\"")
            ##Queries whether there is a username and password match in student table
            qs = query_db("SELECT EXISTS(SELECT student_no,password FROM student WHERE (student_no=\"" + 
            request.form['username'] + "\" AND password=\"" + request.form['password'] + "\")) AS \"col\"")
            t = qi[0]["col"] + qt[0]["col"] + qs[0]["col"]
            if t==0:
                error = 'Invalid credentials'
            elif t==1:
                session['username'] = request.form['username']
                session['password'] = request.form['password']
                return redirect(url_for('home'))
        ##else: register the user then add the user to session and redirect them to home route and handle duplicate username error/ 
        else:
            ##Queries whether username exists already or not
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=\"" + request.form['username'] + "\")) AS \"col\"")
            qt = query_db("SELECT EXISTS(SELECT ta_code FROM ta WHERE (ta_code=\"" + request.form['username'] + "\")) AS \"col\"")
            qs = query_db("SELECT EXISTS(SELECT student_no FROM student WHERE (student_no=\"" + request.form['username'] + "\")) AS \"col\"")
            t = 0
            t = qi[0]["col"] + qt[0]["col"] + qs[0]["col"]
            if t >= 1:
                ##ERROR: user exits 
                error='User already exists'
            elif t == 0:
                ##USER DOES NOT EXIST SO DETERMINE THE USER LEVEL AND CREATE THE RESPECTIVE USER ENTRY
                if request.form['creationcode'] == '0':
                    qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=\"" + request.form['InstructorsCode'] + "\")) AS \"col\"")
                    if (qi[0]["col"] == 1):
                        insert_db("INSERT INTO student (student_no ,first_name ,last_name ,email ,password ,ta_code,instructor_code) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",\"nullTA\",\"{}\")"
                        .format(request.form['username'],request.form['firstname'],request.form['lastname'],request.form['email'],request.form['password'],request.form['InstructorsCode']))
                        session['username'] = request.form['username']
                        session['password'] = request.form['password']
                        return redirect(url_for('home'))
                    else:
                        error="Invalid instructor code"
                elif request.form['creationcode'] =='1':
                    insert_db("INSERT INTO instructor (instructor_code, first_name, last_name, email, password, office_hours, tutorial_hours, office_hours_link, tutorial_link) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",'','','','')"
                        .format(request.form['username'],request.form['firstname'],request.form['lastname'],request.form['email'],request.form['password']))
                    session['username'] = request.form['username']
                    session['password'] = request.form['password']
                    return redirect(url_for('home'))
                elif request.form['creationcode'] == '2':
                    insert_db("INSERT INTO ta (ta_code,first_name ,last_name ,email ,password ,office_hours ,tutorial_hours ,office_hours_link,tutorial_link) VALUES (\"{}\",\"{}\",\"{}\",\"{}\",\"{}\",'','','','')"
                        .format(request.form['username'],request.form['firstname'],request.form['lastname'],request.form['email'],request.form['password']))
                    session['username'] = request.form['username']
                    session['password'] = request.form['password']
                    return redirect(url_for('home'))
                else:
                    error='invalid user type'
    print(error)
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