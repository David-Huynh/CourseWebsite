import sqlite3
from flask import Flask, render_template, session, url_for, redirect, request, flash, g, make_response
app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')
import base64

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
## PDF DOWNLOADER
@app.route('/pdfs/<id>')
def get_pdf(id=None):
    if 'username' in session and 'password' in session:
        if id is not None:
            pdf = query_db("SELECT pdf_name, pdf_data, username FROM pdf WHERE pdf_id=?",[id])
            if pdf:
                if pdf[0]["username"] == session["username"] or pdf[0]["username"] == None:
                    response = make_response(pdf[0]["pdf_data"])
                    response.headers['Content-Type'] = 'application/pdf'
                    response.headers['Content-Disposition'] = \
                        'inline; filename=%s.pdf' % pdf[0]["pdf_name"]
                    return response
                else:
                    return "ERROR: you do not have permission to view this file"
            else:
                return "ERROR: no such file exists"
    return redirect(url_for('login'))
##WEB APP ROUTES
@app.route('/')
def home():
    if 'username' in session and 'password' in session:
        name = query_db("SELECT first_name FROM (SELECT instructor_code as username,first_name FROM instructor UNION SELECT ta_code as username,first_name FROM ta UNION SELECT student_no as username,first_name FROM student) WHERE username=?",[session['username']])
        tas = query_db("SELECT * FROM ta")
        student = query_db("SELECT * FROM student WHERE student_no=?",[session['username']])
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
        if qi[0]["col"] == 1:
            instructor = None
        elif qt[0]["col"] == 1:
            instructor = None
        else:
            instructor = query_db("SELECT * FROM instructor WHERE instructor_code=?",[student[0]["instructor_code"]])
            instructor[0]["first_name"] = instructor[0]["first_name"].lower().capitalize()
            instructor[0]["last_name"] = instructor[0]["last_name"].lower().capitalize()
            if instructor[0]["instructor_picture"] != None:
                instructor[0]["instructor_picture"] = base64.encodebytes(instructor[0]["instructor_picture"])
        for ta in tas:
            ta["first_name"] =  ta["first_name"].lower().capitalize()
            ta["last_name"] =  ta["last_name"].lower().capitalize()
            if ta["ta_picture"] != None:
                ta["ta_picture"]= base64.encodebytes(ta["ta_picture"])
        if instructor:
            return render_template("index.html", name=name[0]["first_name"].lower().capitalize(), tas=tas, instructor=instructor, pdf=instructor[0]["syllabus_id"])
        else:
            return render_template("index.html", name=name[0]["first_name"].lower().capitalize(), tas=tas, instructor=instructor, pdf=None)
    return redirect(url_for('login'))

@app.route('/lectures', methods=['GET', 'POST'])
def lectures():
    if 'username' in session and 'password' in session:
        student=None
        error=None
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
        ##Instructor User Page
        if qi[0]["col"] == 1:
            instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [session["username"]])
            general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
            instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [session["username"]])
            if request.method == 'POST':
                ## Course Wide PDF Upload
                if request.files.get("courseWidePdf"):
                    if request.files["courseWidePdf"]:
                        #Inserts pdfs
                        insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["courseWidePdf"].filename, request.files["courseWidePdf"].read(), session['username']])
                        insert_db("INSERT INTO lec_pdfs (week, pdf_id) VALUES (?,(SELECT last_insert_rowid()))",[request.form["week"]])
                ## else: Lecture Upload
                else:
                    ##Checks whether selected week lecture exists
                    lectureExists = query_db("SELECT EXISTS(SELECT * FROM lectures WHERE (week=? AND instructor_code=?)) AS \"col\"",[request.form["week"],session['username']])
                    if lectureExists[0]["col"] !=1:
                        ## Insert if lecture does not exist
                        insert_db("INSERT INTO lectures (week, lecture_title,instructor_code) VALUES (?,?,?)",[request.form["week"],request.form["lecture_title"], session['username']])
                    else:
                        ## Update if lecture does not exist
                        insert_db("UPDATE lectures SET lecture_title=? WHERE week=? AND instructor_code=?",[request.form["lecture_title"], request.form["week"],session['username']])
                    if request.form["tues_recording"]:
                        ## Updates tues_recording
                        insert_db("UPDATE lectures SET tues_recording=? WHERE week=? AND instructor_code=?",[request.form["tues_recording"],request.form["week"], session['username']])
                    if request.form["thurs_recording"]:
                        ## Updates thurs_recording
                        insert_db("UPDATE lectures SET thurs_recording=? WHERE week=? AND instructor_code=?",[request.form["thurs_recording"],request.form["week"], session['username']])
                    ##INSERT FILES INTO DATABASE
                    if request.files["instructor_pdf"]:
                        ##INSERTS PDFS INTO DATABASE AND REMOVES OLD PDFS IF APPLICABLE
                        instructor_Notes = query_db("SELECT pdf_id FROM instr_notes WHERE (week=? AND instructor_code=?)",[request.form["week"],session['username']])
                        for note in instructor_Notes:
                            ##removes all old pdfs
                            insert_db("DELETE FROM pdf WHERE pdf_id=?",[note["pdf_id"]])
                        if len(instructor_Notes) >=1:
                            ##Deletes all refernces
                            insert_db("DELETE FROM instr_notes WHERE week=? AND instructor_code=?",[request.form["week"], session['username']])
                        for pdf in request.files.getlist("instructor_pdf"):
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[pdf.filename, pdf.read(), session['username']])
                            insert_db("INSERT INTO instr_notes (week, instructor_code, pdf_id) VALUES (?,?,(SELECT last_insert_rowid()))",[request.form["week"],session['username']])
            return render_template("lectures.html", 
                instructor_lecture_material=instructor_lecture_material,  
                general_lecture_material=general_lecture_material, 
                instructor_pdfs=instructor_pdfs,
                instructor=qi)
        ##TA User Page
        elif qt[0]["col"] == 1:
            first_instructor_code = query_db("SELECT instructor_code FROM instructor")[0]
            instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [first_instructor_code["instructor_code"]])
            general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
            instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [first_instructor_code["instructor_code"]])
            return render_template("lectures.html",
                instructor_lecture_material=instructor_lecture_material,  
                general_lecture_material=general_lecture_material, 
                instructor_pdfs=instructor_pdfs)
        ##Student User Page
        else:
            student = query_db("SELECT * FROM student WHERE student_no=?",[session['username']])
            instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [student[0]["instructor_code"]])
            general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
            instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [student[0]["instructor_code"]])
            return render_template("lectures.html", 
                instructor_lecture_material=instructor_lecture_material,  
                general_lecture_material=general_lecture_material, 
                instructor_pdfs=instructor_pdfs)
        return render_template("lectures.html")
    return redirect(url_for('login'))
@app.route('/tutorials', methods=['GET', 'POST'])
def tutorials():
    if 'username' in session and 'password' in session:
        return render_template("tutorials.html")
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
@app.route('/feedback')
def feedback():
    if 'username' in session and 'password' in session:
        return render_template("feedback.html")
    return redirect(url_for('login'))
@app.route('/profile')
def profile():
    if 'username' in session and 'password' in session:
        fname = query_db("SELECT first_name FROM instructor WHERE instructor_code=?",[session['username']])
        lname = query_db("SELECT last_name FROM instructor WHERE instructor_code=?",[session['username']])
        if fname and lname:
            return render_template("profile.html", name=fname[0]["first_name"].lower().capitalize()+' '+lname[0]["last_name"].lower().capitalize(), instructor=None)
        return render_template("profile.html", instructor=None)
    return redirect(url_for('login'))
##LOGIN/SIGNUP REQUESTS
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        ## IF REQUEST = LOGIN
        if request.form['firstname'] == '' and request.form['lastname'] == '':
            ##Queries whether there is a username and password match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code,password FROM instructor WHERE (instructor_code=? AND password=?)) AS \"col\"",[request.form["username"],request.form["password"]])
            ##Queries whether there is a username and password match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=? AND password=?)) AS \"col\"",[request.form["username"],request.form["password"]])
            ##Queries whether there is a username and password match in student table
            qs = query_db("SELECT EXISTS(SELECT student_no,password FROM student WHERE (student_no=? AND password=?)) AS \"col\"",[request.form["username"],request.form["password"]])
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
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[request.form['username']])
            qt = query_db("SELECT EXISTS(SELECT ta_code FROM ta WHERE (ta_code=?)) AS \"col\"",[request.form['username']])
            qs = query_db("SELECT EXISTS(SELECT student_no FROM student WHERE (student_no=?)) AS \"col\"",[request.form['username']])
            t = 0
            t = qi[0]["col"] + qt[0]["col"] + qs[0]["col"]
            if t >= 1:
                ##ERROR: user exits 
                error='User already exists'
            elif t == 0:
                ##USER DOES NOT EXIST SO DETERMINE THE USER LEVEL AND CREATE THE RESPECTIVE USER ENTRY
                if request.form['creationcode'] == '0' and request.form['InstructorsCode']:
                    qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[request.form['InstructorsCode']])
                    if (qi[0]["col"] == 1):
                        insert_db("INSERT INTO student (student_no ,first_name ,last_name ,email ,password,instructor_code) VALUES (?,?,?,?,?,?)",
                        [request.form['username'],request.form['firstname'],request.form['lastname'],request.form['email'],request.form['password'],request.form['InstructorsCode']])
                        session['username'] = request.form['username']
                        session['password'] = request.form['password']
                        return redirect(url_for('home'))
                    else:
                        error="Invalid instructor code"
                elif request.form['creationcode'] =='1' and not request.form['InstructorsCode']:
                    insert_db("INSERT INTO instructor (instructor_code, first_name, last_name, email, password) VALUES (?,?,?,?,?)",
                        [request.form['username'],request.form['firstname'],request.form['lastname'],request.form['email'],request.form['password']])
                    session['username'] = request.form['username']
                    session['password'] = request.form['password']
                    return redirect(url_for('home'))
                elif request.form['creationcode'] == '2' and not request.form['InstructorsCode']:
                    insert_db("INSERT INTO ta (ta_code,first_name ,last_name ,email ,password) VALUES (?,?,?,?,?)",
                        [request.form['username'],request.form['firstname'],request.form['lastname'],request.form['email'],request.form['password']])
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