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

##Injects instructor and ta information into context of every template (Defaults to first ta and instructor in database if none set)
@app.context_processor
def inject_ta_instructor():
    if 'username' in session and 'password' in session:
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
        first_instructor = query_db("SELECT instructor_code FROM instructor",one=True)
        first_ta = query_db("SELECT ta_code FROM ta",one=True)
        if qi[0]["col"] == 1:
            return dict(ta_id=first_ta["ta_code"],instructor_id=session['username'])
        elif qt[0]["col"] == 1:
            return dict(ta_id=session['username'],instructor_id=first_instructor["instructor_code"])
        else:
            student = query_db("SELECT * FROM student WHERE (student_no=?)",[session['username']])
            if student[0]["ta_code"] and student[0]["instructor_code"]:
                return dict(ta_id=student[0]["ta_code"],instructor_id=student[0]["instructor_code"])
            elif student[0]["ta_code"] and not student[0]["instructor_code"]:
                return dict(ta_id=student[0]["ta_code"], instructor_id=first_instructor["instructor_code"])
            elif student[0]["instructor_code"] and not student[0]["ta_code"]:
                return dict(ta_id=first_ta["ta_code"], instructor_id=student[0]["instructor_code"])
            return dict(ta_id=first_ta["ta_code"], instructor_id=first_instructor["instructor_code"])
    return dict()

## ON APPLICATION CLOSE
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

## PDF Display Route
@app.route('/pdfs/<id>')
def get_pdf(id=None):
    if 'username' in session and 'password' in session:
        if id is not None:
            pdf = query_db("SELECT pdf_name, pdf_data, username FROM pdf WHERE pdf_id=?",[id])
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
            student = query_db("SELECT EXISTS(SELECT * FROM student WHERE student_no=?) AS \"col\"",[pdf[0]["username"]])
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
            if pdf:
                if pdf[0]["username"] == session["username"] or pdf[0]["username"] == "all" or qi[0]["col"] == 1 or (student[0]["col"] == 1 and qt[0]["col"]):
                    print(type(pdf[0]["pdf_data"]))
                    response = make_response(bytes(pdf[0]["pdf_data"]))
                    response.headers['Content-Type'] = "application/pdf"
                    response.headers['Content-Disposition'] = "inline; filename={}.pdf".format(pdf[0]["pdf_name"])
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

@app.route('/lectures/<id>', methods=['GET', 'POST'])
def lectures(id=None):
    if 'username' in session and 'password' in session:
        if id is not None:
            ##Queries whether there is a username match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
            ##Queries whether there is a username match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
            ##Instructor User Page
            if qi[0]["col"] == 1:
                instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [id])
                general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
                instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [id])
                if session["username"] == id:
                    if request.method == 'POST':
                        ## Course Wide PDF Upload
                        if request.files.get("courseWidePdf"):
                            if request.files["courseWidePdf"]:
                                #Inserts pdfs
                                insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["courseWidePdf"].filename, request.files["courseWidePdf"].read(), "all"])
                                insert_db("INSERT INTO lec_pdfs (week, pdf_id) VALUES (?,(SELECT last_insert_rowid()))",[request.form["week"]])
                                return redirect(url_for(".lectures",id=id))
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
                                    insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[pdf.filename, pdf.read(), "all"])
                                    insert_db("INSERT INTO instr_notes (week, instructor_code, pdf_id) VALUES (?,?,(SELECT last_insert_rowid()))",[request.form["week"],"all"])
                            return redirect(url_for(".lectures",id=id))
                    return render_template("lectures.html", 
                        instructor_lecture_material=instructor_lecture_material,  
                        general_lecture_material=general_lecture_material, 
                        instructor_pdfs=instructor_pdfs,
                        instructor=qi,
                        id=id)
                return render_template("lectures.html", 
                        instructor_lecture_material=instructor_lecture_material,  
                        general_lecture_material=general_lecture_material, 
                        instructor_pdfs=instructor_pdfs,
                        id=id)
            ##TA User Page
            elif qt[0]["col"] == 1:
                instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [id])
                general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
                instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [id])
                return render_template("lectures.html",
                    instructor_lecture_material=instructor_lecture_material,  
                    general_lecture_material=general_lecture_material, 
                    instructor_pdfs=instructor_pdfs,
                    id=id)
            ##Student User Page
            else:
                instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [id])
                general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
                instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [id])
                return render_template("lectures.html", 
                    instructor_lecture_material=instructor_lecture_material,  
                    general_lecture_material=general_lecture_material, 
                    instructor_pdfs=instructor_pdfs,
                    id=id)
            return render_template("lectures.html")
    return redirect(url_for('login'))

@app.route('/tutorials/<id>', methods=['GET', 'POST'])
def tutorials(id=None):
    if 'username' in session and 'password' in session:
        if id is not None:
            ##Queries whether there is a username match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
            ##Queries whether there is a username match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
            ##Instructor User Page
            if qi[0]["col"] == 1:
                ta_tutorial_material = query_db("SELECT * FROM tutorials WHERE ta_code=? ORDER BY week ASC", [id])
                general_tutorial_material = query_db("SELECT * FROM tut_pdfs INNER JOIN pdf ON tut_pdfs.pdf_id = pdf.pdf_id")
                ta_pdfs = query_db("SELECT * FROM ta_notes INNER JOIN pdf ON ta_notes.pdf_id = pdf.pdf_id WHERE ta_code=?", [id])
                if request.method == 'POST':
                    if request.files.get("courseWideTutPdf"):
                        #Inserts pdfs
                        insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["courseWideTutPdf"].filename, request.files["courseWideTutPdf"].read(), "all"])
                        insert_db("INSERT INTO tut_pdfs (week, pdf_id) VALUES (?,(SELECT last_insert_rowid()))",[request.form["week"]])
                        return redirect(url_for(".tutorials",id=id))
                return render_template("tutorials.html", 
                    ta_tutorial_material=ta_tutorial_material,  
                    general_tutorial_material=general_tutorial_material, 
                    ta_pdfs=ta_pdfs,
                    qi=qi,
                    id=id)
            ##TA User Page
            elif qt[0]["col"] == 1:
                ta_tutorial_material = query_db("SELECT * FROM tutorials WHERE ta_code=? ORDER BY week ASC", [id])
                general_tutorial_material = query_db("SELECT * FROM tut_pdfs INNER JOIN pdf ON tut_pdfs.pdf_id = pdf.pdf_id")
                ta_pdfs = query_db("SELECT * FROM ta_notes INNER JOIN pdf ON ta_notes.pdf_id = pdf.pdf_id WHERE ta_code=?", [id])
                if session["username"] == id:
                    if request.method == 'POST':
                        if request.files.get("courseWideTutPdf"):
                            #Inserts pdfs
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["courseWideTutPdf"].filename, request.files["courseWideTutPdf"].read(), "all"])
                            insert_db("INSERT INTO tut_pdfs (week, pdf_id) VALUES (?,(SELECT last_insert_rowid()))",[request.form["week"]])
                        else:
                            ##Checks whether selected week tutorial exists
                            tutorialExists = query_db("SELECT EXISTS(SELECT * FROM tutorials WHERE (week=? AND ta_code=?)) AS \"col\"",[request.form["week"],session['username']])
                            if tutorialExists[0]["col"] !=1:
                                ## Insert if tutorial does not exist
                                insert_db("INSERT INTO tutorials (week,ta_code) VALUES (?,?)",[request.form["week"], session['username']])
                            if request.form["recording_link"]:
                                ## Updates recording link
                                insert_db("UPDATE tutorials SET recording_link=? WHERE week=? AND ta_code=?",[request.form["recording_link"],request.form["week"], session['username']])
                            ##INSERT FILES INTO DATABASE
                            if request.files["ta_pdf"]:
                                ##INSERTS PDFS INTO DATABASE AND REMOVES OLD PDFS IF APPLICABLE
                                ta_Notes = query_db("SELECT pdf_id FROM ta_notes WHERE (week=? AND ta_code=?)",[request.form["week"],session['username']])
                                for note in ta_Notes:
                                    ##removes all old pdfs
                                    insert_db("DELETE FROM pdf WHERE pdf_id=?",[note["pdf_id"]])
                                if len(ta_Notes) >=1:
                                    ##Deletes all refernces
                                    insert_db("DELETE FROM ta_notes WHERE week=? AND ta_code=?",[request.form["week"], session['username']])
                                for pdf in request.files.getlist("ta_pdf"):
                                    insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[pdf.filename, pdf.read(), "all"])
                                    insert_db("INSERT INTO ta_notes (week, ta_code, pdf_id) VALUES (?,?,(SELECT last_insert_rowid()))",[request.form["week"],"all"])
                        return redirect(url_for(".tutorials",id=id))
                    return render_template("tutorials.html",
                        ta_tutorial_material=ta_tutorial_material,  
                        general_tutorial_material=general_tutorial_material, 
                        ta_pdfs=ta_pdfs, 
                        ta=qt,
                        id=id)
                return render_template("tutorials.html",
                        ta_tutorial_material=ta_tutorial_material,  
                        general_tutorial_material=general_tutorial_material, 
                        ta_pdfs=ta_pdfs,
                        id=id)
            ##Student User Page
            else:
                ta_tutorial_material = query_db("SELECT * FROM tutorials WHERE ta_code=? ORDER BY week ASC", [id])
                general_tutorial_material = query_db("SELECT * FROM tut_pdfs INNER JOIN pdf ON tut_pdfs.pdf_id = pdf.pdf_id")
                ta_pdfs = query_db("SELECT * FROM ta_notes INNER JOIN pdf ON ta_notes.pdf_id = pdf.pdf_id WHERE ta_code=?", [id])
                return render_template("tutorials.html", 
                    ta_tutorial_material=ta_tutorial_material,  
                    general_tutorial_material=general_tutorial_material, 
                    ta_pdfs=ta_pdfs,
                    id=id)
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

@app.route('/profile', methods=['GET','POST'])
def profile():
    if 'username' in session and 'password' in session:
        if id is not None:
            ##Queries whether there is a username match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session['username']])
            ##Queries whether there is a username match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session['username']])
            # Load Instructor page
            if qi[0]["col"] == 1:
                instructor_info = query_db("SELECT * FROM instructor WHERE instructor_code=?",[session['username']])
                syllabus = query_db("SELECT * FROM pdf INNER JOIN instructor ON instructor.syllabus_id = pdf.pdf_id AND instructor.instructor_code=?", [session['username']])
                """instructor_info = query_db("SELECT * FROM instructor WHERE instructor_code=?",[session['username']])
                syllabus_id = query_db("SELECT pdf.id FROM instructor, pdf WHERE instructor_code=? AND pdf.pdf_id=instructor.syllabus_id;",[session['username']])
                syllabus_name = query_db("SELECT pdf.pdf_name FROM instructor, pdf WHERE instructor_code=? AND pdf.pdf_id=instructor.syllabus_id;",[session['username']])"""
                if request.method == 'POST':
                    #update form info case
                    return "updating info for instructor"
                return render_template("profile.html", 
                    user_type=0,
                    user_info=instructor_info,
                    syllabus=syllabus)
            # Load TA page
            elif qt[0]["col"] == 1:
                ta_info = query_db("SELECT * FROM ta WHERE ta_code=?",[session['username']])
                if request.method == 'POST':
                    #update form info case
                    return "updating info for TA"
                return render_template("profile.html", 
                    user_type=1,
                    user_info=ta_info)
            # Load Student page
            else:
                prof_list = query_db("SELECT instructor_code, first_name, last_name FROM instructor")
                ta_list = query_db("SELECT ta_code, first_name, last_name FROM ta")
                stud_info = query_db("SELECT * FROM student WHERE student_no=?",[session['username']])
                if request.method == 'POST':
                    return 'updating data for student'
                return render_template("profile.html",
                    user_type=2,
                    user_info=stud_info, 
                    prof_list=prof_list,
                    ta_list=ta_list)    
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