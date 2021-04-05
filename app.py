from flask import Flask, render_template, session, url_for, redirect, request, flash, g, make_response
import sqlite3

import base64
import json
from datetime import datetime

app = Flask(__name__, template_folder="./src/templates", static_folder="./src/static")
app.secret_key = "b'\x1a\xe3$e=(\xdc$\xf6\x95}\x00z\x1c\xae\xc2\n\x1a\x08\x85\x1f#9M\xff\xef=x\rg\x9c\xc9'"
DATABASE = "./assignment3.db"

##DATABASE CONNECTION AND QUERY
def make_dicts(cursor, row):
    return dict((cursor.description[idx][0], value)
                for idx, value in enumerate(row))
def get_db():
    db = getattr(g, "_database", None)
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
    if "username" in session :
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
        first_instructor = query_db("SELECT instructor_code FROM instructor",one=True)
        first_ta = query_db("SELECT ta_code FROM ta",one=True)
        if qi[0]["col"] == 1:
            return dict(ta_id=first_ta["ta_code"],instructor_id=session["username"],ta_level=True)
        elif qt[0]["col"] == 1:
            return dict(ta_id=session["username"],instructor_id=first_instructor["instructor_code"],ta_level=True)
        else:
            student = query_db("SELECT * FROM student WHERE (student_no=?)",[session["username"]])
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
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

## PDF Display Route
@app.route("/pdfs/<id>")
def get_pdf(id=None):
    if "username" in session :
        if id is not None:
            pdf = query_db("SELECT pdf_name, pdf_data, username FROM pdf WHERE pdf_id=?",[id])
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
            student = query_db("SELECT EXISTS(SELECT * FROM student WHERE student_no=?) AS \"col\"",[pdf[0]["username"]])
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
            if pdf:
                if pdf[0]["username"] == session["username"] or pdf[0]["username"] == "all" or qi[0]["col"] == 1 or (student[0]["col"] == 1 and qt[0]["col"]):
                    print(type(pdf[0]["pdf_data"]))
                    response = make_response(bytes(pdf[0]["pdf_data"]))
                    response.headers["Content-Type"] = "application/pdf"
                    response.headers["Content-Disposition"] = "inline; filename={}.pdf".format(pdf[0]["pdf_name"])
                    return response
                else:
                    return "ERROR: you do not have permission to view this file"
            else:
                return "ERROR: no such file exists"
    return redirect(url_for("login"))
## Route for instructors/tas to submit marks
@app.route("/submitMarks", methods=["POST"])
def submitMarks():
    if "username" in session :
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
        ## Only allow requests from instructors or tas
        if qi[0]["col"]==1 or qt[0]["col"]==1:
            if request.method == "POST":
                print(request.json)
                if request.json["type"] == "assignment":
                    insert_db("UPDATE assignment_submissions SET grade=?, marked=1, regrade_requested=0 WHERE assignment_no=? AND student_no=?",[request.json["grade"], request.json["assessment_no"], request.json["student_no"]])
                elif request.json["type"] == "test":
                    insert_db("UPDATE test_submissions SET grade=?, marked=1, regrade_requested=0 WHERE test_no=? AND student_no=?",[request.json["grade"], request.json["assessment_no"], request.json["student_no"]])
                response = make_response(json.dumps({"nothing":"nothing"}))
                response.headers["Content-Type"] = "application/json"
                return response

##WEB APP ROUTES
@app.route("/")
def home():
    if "username" in session :
        name = query_db("SELECT first_name FROM (SELECT instructor_code as username,first_name FROM instructor UNION SELECT ta_code as username,first_name FROM ta UNION SELECT student_no as username,first_name FROM student) WHERE username=?",[session["username"]])
        tas = query_db("SELECT * FROM ta")
        student = query_db("SELECT * FROM student WHERE student_no=?",[session["username"]])
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
        if qi[0]["col"] == 1:
            instructor = None
        elif qt[0]["col"] == 1:
            instructor = None
        else:
            instructor = query_db("SELECT * FROM instructor WHERE instructor_code=?",[student[0]["instructor_code"]])
            instructor[0]["first_name"] = instructor[0]["first_name"].lower().capitalize()
            instructor[0]["last_name"] = instructor[0]["last_name"].lower().capitalize()
            if instructor[0]["instructor_picture"] != None:
                instructor[0]["instructor_picture"] = base64.b64encode(instructor[0]["instructor_picture"]).decode("ascii")
        for ta in tas:
            ta["first_name"] = ta["first_name"].lower().capitalize()
            ta["last_name"] = ta["last_name"].lower().capitalize()
            if ta["ta_picture"] != None:
                ta["ta_picture"]= base64.b64encode(ta["ta_picture"]).decode("ascii")
        if instructor:
            return render_template("index.html", name=name[0]["first_name"].lower().capitalize(), tas=tas, instructor=instructor, pdf=instructor[0]["syllabus_id"])
        else:
            return render_template("index.html", name=name[0]["first_name"].lower().capitalize(), tas=tas, instructor=instructor, pdf=None)
    return redirect(url_for("login"))
##Marks Route
@app.route("/marking")
def marking():
    if "username" in session :
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
        ## Only show page to instructors or tas
        if qi[0]["col"]==1 or qt[0]["col"]==1:
            assignments = query_db("SELECT * FROM assignments ORDER BY assignment_no ASC")
            assignments_submissions = query_db("SELECT * FROM assignment_submissions ORDER BY assignment_no ASC")
            tests = query_db("SELECT * FROM tests ORDER BY test_no ASC")
            tests_submissions = query_db("SELECT * FROM test_submissions ORDER BY test_no ASC")
            return render_template("marking.html", 
                assignments=assignments,
                assignments_submissions=assignments_submissions,
                tests=tests,
                tests_submissions=tests_submissions)
        else:
            return "ERROR: insufficient permission to view this page"
    return redirect(url_for("login"))


@app.route("/lectures/<id>", methods=["GET", "POST"])
def lectures(id=None):
    if "username" in session :
        if id is not None:
            ##Queries whether there is a username match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
            ##Queries whether there is a username match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
            ##Instructor name
            name = query_db("SELECT first_name FROM instructor WHERE instructor_code=?",[id],one=True)["first_name"].lower().capitalize()
            ##Instructor User Page
            if qi[0]["col"] == 1:
                instructor_lecture_material = query_db("SELECT * FROM lectures WHERE instructor_code=? ORDER BY week ASC", [id])
                general_lecture_material = query_db("SELECT * FROM lec_pdfs INNER JOIN pdf ON lec_pdfs.pdf_id = pdf.pdf_id")
                instructor_pdfs = query_db("SELECT * FROM instr_notes INNER JOIN pdf ON instr_notes.pdf_id = pdf.pdf_id WHERE instructor_code=?", [id])
                if session["username"] == id:
                    if request.method == "POST":
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
                            lectureExists = query_db("SELECT EXISTS(SELECT * FROM lectures WHERE (week=? AND instructor_code=?)) AS \"col\"",[request.form["week"],session["username"]])
                            if lectureExists[0]["col"] !=1:
                                ## Insert if lecture does not exist
                                insert_db("INSERT INTO lectures (week, lecture_title,instructor_code) VALUES (?,?,?)",[request.form["week"],request.form["lecture_title"], session["username"]])
                            else:
                                ## Update if lecture does not exist
                                insert_db("UPDATE lectures SET lecture_title=? WHERE week=? AND instructor_code=?",[request.form["lecture_title"], request.form["week"],session["username"]])
                            if request.form["tues_recording"]:
                                ## Updates tues_recording
                                insert_db("UPDATE lectures SET tues_recording=? WHERE week=? AND instructor_code=?",[request.form["tues_recording"],request.form["week"], session["username"]])
                            if request.form["thurs_recording"]:
                                ## Updates thurs_recording
                                insert_db("UPDATE lectures SET thurs_recording=? WHERE week=? AND instructor_code=?",[request.form["thurs_recording"],request.form["week"], session["username"]])
                            ##INSERT FILES INTO DATABASE
                            if request.files["instructor_pdf"]:
                                ##INSERTS PDFS INTO DATABASE AND REMOVES OLD PDFS IF APPLICABLE
                                instructor_Notes = query_db("SELECT pdf_id FROM instr_notes WHERE (week=? AND instructor_code=?)",[request.form["week"],session["username"]])
                                for note in instructor_Notes:
                                    ##removes all old pdfs
                                    insert_db("DELETE FROM pdf WHERE pdf_id=?",[note["pdf_id"]])
                                if len(instructor_Notes) >=1:
                                    ##Deletes all refernces
                                    insert_db("DELETE FROM instr_notes WHERE week=? AND instructor_code=?",[request.form["week"], session["username"]])
                                for pdf in request.files.getlist("instructor_pdf"):
                                    insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[pdf.filename, pdf.read(), "all"])
                                    insert_db("INSERT INTO instr_notes (week, instructor_code, pdf_id) VALUES (?,?,(SELECT last_insert_rowid()))",[request.form["week"],session["username"]])
                            return redirect(url_for(".lectures",id=id))
                    return render_template("lectures.html", 
                        instructor_lecture_material=instructor_lecture_material,  
                        general_lecture_material=general_lecture_material, 
                        instructor_pdfs=instructor_pdfs,
                        instructor=qi,
                        name=name,
                        id=id)
                return render_template("lectures.html", 
                        instructor_lecture_material=instructor_lecture_material,  
                        general_lecture_material=general_lecture_material, 
                        instructor_pdfs=instructor_pdfs,
                        name=name,
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
                    name=name,
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
                    name=name,
                    id=id)
            return render_template("lectures.html")
    return redirect(url_for("login"))

@app.route("/tutorials/<id>", methods=["GET", "POST"])
def tutorials(id=None):
    if "username" in session :
        if id is not None:
            ##Queries whether there is a username match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
            ##Queries whether there is a username match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
            ##Query Ta Name
            name = query_db("SELECT first_name FROM ta WHERE ta_code=?",[id],one=True)["first_name"].lower().capitalize()
            ##Instructor User Page
            if qi[0]["col"] == 1:
                ta_tutorial_material = query_db("SELECT * FROM tutorials WHERE ta_code=? ORDER BY week ASC", [id])
                general_tutorial_material = query_db("SELECT * FROM tut_pdfs INNER JOIN pdf ON tut_pdfs.pdf_id = pdf.pdf_id")
                ta_pdfs = query_db("SELECT * FROM ta_notes INNER JOIN pdf ON ta_notes.pdf_id = pdf.pdf_id WHERE ta_code=?", [id])
                if request.method == "POST":
                    if request.form.get("courseWideTutPdf"):
                        #Inserts pdfs
                        insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["courseWideTutPdf"].filename, request.files["courseWideTutPdf"].read(), "all"])
                        insert_db("INSERT INTO tut_pdfs (week, pdf_id) VALUES (?,(SELECT last_insert_rowid()))",[request.form["week"]])
                    else:
                        flash("No such post request supported")
                    return redirect(url_for(".tutorials",id=id))
                return render_template("tutorials.html", 
                    ta_tutorial_material=ta_tutorial_material,  
                    general_tutorial_material=general_tutorial_material, 
                    ta_pdfs=ta_pdfs,
                    name=name,
                    qi=qi,
                    id=id)
            ##TA User Page
            elif qt[0]["col"] == 1:
                ta_tutorial_material = query_db("SELECT * FROM tutorials WHERE ta_code=? ORDER BY week ASC", [id])
                general_tutorial_material = query_db("SELECT * FROM tut_pdfs INNER JOIN pdf ON tut_pdfs.pdf_id = pdf.pdf_id")
                ta_pdfs = query_db("SELECT * FROM ta_notes INNER JOIN pdf ON ta_notes.pdf_id = pdf.pdf_id WHERE ta_code=?", [id])
                if session["username"] == id:
                    if request.method == "POST":
                        if request.files.get("courseWideTutPdf"):
                            #Inserts pdfs
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["courseWideTutPdf"].filename, request.files["courseWideTutPdf"].read(), "all"])
                            insert_db("INSERT INTO tut_pdfs (week, pdf_id) VALUES (?,(SELECT last_insert_rowid()))",[request.form["week"]])
                        else:
                            ##Checks whether selected week tutorial exists
                            tutorialExists = query_db("SELECT EXISTS(SELECT * FROM tutorials WHERE (week=? AND ta_code=?)) AS \"col\"",[request.form["week"],session["username"]])
                            if tutorialExists[0]["col"] !=1:
                                ## Insert if tutorial does not exist
                                insert_db("INSERT INTO tutorials (week,ta_code) VALUES (?,?)",[request.form["week"], session["username"]])
                            if request.form["recording_link"]:
                                ## Updates recording link
                                insert_db("UPDATE tutorials SET recording_link=? WHERE week=? AND ta_code=?",[request.form["recording_link"],request.form["week"], session["username"]])
                            ##INSERT FILES INTO DATABASE
                            if request.files["ta_pdf"]:
                                ##INSERTS PDFS INTO DATABASE AND REMOVES OLD PDFS IF APPLICABLE
                                ta_Notes = query_db("SELECT pdf_id FROM ta_notes WHERE (week=? AND ta_code=?)",[request.form["week"],session["username"]])
                                for note in ta_Notes:
                                    ##removes all old pdfs
                                    insert_db("DELETE FROM pdf WHERE pdf_id=?",[note["pdf_id"]])
                                if len(ta_Notes) >=1:
                                    ##Deletes all refernces
                                    insert_db("DELETE FROM ta_notes WHERE week=? AND ta_code=?",[request.form["week"], session["username"]])
                                for pdf in request.files.getlist("ta_pdf"):
                                    insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[pdf.filename, pdf.read(), "all"])
                                    insert_db("INSERT INTO ta_notes (week, ta_code, pdf_id) VALUES (?,?,(SELECT last_insert_rowid()))",[request.form["week"],session["username"]])
                        return redirect(url_for(".tutorials",id=id))
                    return render_template("tutorials.html",
                        ta_tutorial_material=ta_tutorial_material,  
                        general_tutorial_material=general_tutorial_material, 
                        ta_pdfs=ta_pdfs, 
                        name=name,
                        ta=qt,
                        id=id)
                return render_template("tutorials.html",
                        ta_tutorial_material=ta_tutorial_material,  
                        general_tutorial_material=general_tutorial_material, 
                        name=name,
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
                    name=name,
                    ta_pdfs=ta_pdfs,
                    id=id)
            return render_template("tutorials.html")
    return redirect(url_for("login"))

@app.route("/coursework", methods=["GET", "POST"])
def coursework():
    if "username" in session :
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
        assignments = query_db("SELECT * FROM assignments ORDER BY assignment_no ASC")
        tests = query_db("SELECT * FROM tests ORDER BY test_no ASC")
        ##Instructor User Page
        if qi[0]["col"] == 1:
            if request.method == "POST":
                if "assignment_no" in request.form:
                    ##Checks whether selected assignment exists
                    assignmentExists = query_db("SELECT * FROM assignments WHERE (assignment_no=?)",[request.form["assignment_no"]],one=True)
                    if not assignmentExists:
                        insert_db("INSERT INTO assignments (assignment_no) VALUES (?)",[request.form["assignment_no"]])
                        assignmentExists = query_db("SELECT * FROM assignments WHERE (assignment_no=?)",[request.form["assignment_no"]],one=True)
                    if request.files.get("assignment_pdf"): 
                        if not assignmentExists["pdf_id"]:
                            ## Insert if assignment does not exist
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["assignment_pdf"].filename, request.files["assignment_pdf"].read(), "all"])
                            insert_db("UPDATE assignments SET pdf_id=(SELECT last_insert_rowid()) WHERE assignment_no=?",[request.form["assignment_no"]])
                        elif assignmentExists["pdf_id"]:
                            insert_db("UPDATE pdf SET pdf_name=?,pdf_data=? WHERE pdf_id=?",[request.files["assignment_pdf"].filename, request.files["assignment_pdf"].read(), assignmentExists["pdf_id"]])
                    if request.files.get("solution_pdf"):
                        if not assignmentExists["solution_id"]:
                            ## Insert if assignment solution does not exist
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["solution_pdf"].filename, request.files["solution_pdf"].read(), "all"])
                            insert_db("UPDATE assignments SET solution_id=(SELECT last_insert_rowid()) WHERE assignment_no=?",[request.form["assignment_no"]])
                        elif assignmentExists["solution_id"]:
                            insert_db("UPDATE pdf SET pdf_name=?,pdf_data=? WHERE pdf_id=?",[request.files["solution_pdf"].filename, request.files["solution_pdf"].read(), assignmentExists["solution_id"]])
                    ## Insert due date
                    insert_db("UPDATE assignments SET due_date=? WHERE assignment_no=?",[request.values["due_date"]+"T"+request.values["due_time"]+":00.00",request.form["assignment_no"]])
                elif "test_no" in request.form:
                    testExists = query_db("SELECT * FROM tests WHERE (test_no=?)",[request.form["test_no"]],one=True)
                    if not testExists:
                        insert_db("INSERT INTO tests (test_no) VALUES (?)",[request.form["test_no"]])
                        testExists = query_db("SELECT * FROM tests WHERE (test_no=?)",[request.form["test_no"]],one=True)
                    if request.files.get("test_pdf"):
                        if not testExists["pdf_id"]:
                            ## Insert if test does not exist
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["test_pdf"].filename, request.files["test_pdf"].read(), "all"])
                            insert_db("UPDATE tests SET pdf_id=(SELECT last_insert_rowid()) WHERE test_no=?",[request.form["test_no"]])
                        elif testExists["pdf_id"]:
                            insert_db("UPDATE pdf SET pdf_name=?,pdf_data=? WHERE pdf_id=?",[request.files["test_pdf"].filename, request.files["test_pdf"].read(), testExists["pdf_id"]])
                    if request.files.get("solution_pdf"):
                        if not testExists["solution_id"]:
                            ## Insert if test solution does not exist
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["solution_pdf"].filename, request.files["solution_pdf"].read(), "all"])
                            insert_db("UPDATE tests SET solution_id=(SELECT last_insert_rowid()) WHERE test_no=?",[request.form["test_no"]])
                        elif testExists["solution_id"]:
                            insert_db("UPDATE pdf SET pdf_name=?,pdf_data=? WHERE pdf_id=?",[request.files["solution_pdf"].filename, request.files["solution_pdf"].read(), testExists["solution_id"]])
                    ## Insert due date
                    insert_db("UPDATE tests SET due_date=? WHERE test_no=?",[request.values["due_date"]+"T"+request.values["due_time"]+":00.00",request.form["test_no"]])
                return redirect(url_for("coursework"))
            return render_template("courseWork.html", 
                assignments=assignments,
                tests=tests,
                qi=qi)
        ##TA User Page
        elif qt[0]["col"] == 1:
            return render_template("courseWork.html",
                assignments=assignments,
                tests=tests)
        ##Student Page
        else:
            assignment_submissions= query_db("SELECT * FROM assignment_submissions WHERE student_no=?",[session["username"]])
            test_submissions =query_db("SELECT * FROM test_submissions WHERE student_no=?",[session["username"]])
            if request.method == "POST":
                now = datetime.now()
                ##Checks whether selected assignment exists
                if "assignment_no" in request.form and "dropmenu" not in request.form:
                    assignment = query_db("SELECT * FROM assignments WHERE (assignment_no=?)",[request.form["assignment_no"]],one=True)
                    if assignment:
                        assignmentExists = query_db("SELECT * FROM assignment_submissions WHERE assignment_no=? AND student_no=?",[request.form["assignment_no"],session["username"]],one=True)
                        if not assignmentExists:
                            ##Inserts username into row first
                            insert_db("INSERT INTO assignment_submissions (assignment_no,student_no,marked) VALUES (?,?,0)",[request.form["assignment_no"],session["username"]])
                            assignmentExists = query_db("SELECT * FROM assignment_submissions WHERE student_no=? AND assignment_no=?",[session["username"], request.form["assignment_no"]],one=True)
                        if request.files.get("assignment_pdf"):
                            if not assignmentExists["pdf_id"]:
                                ## Insert if assignment does not exist
                                insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["assignment_pdf"].filename, request.files["assignment_pdf"].read(), session["username"]])
                                insert_db("UPDATE assignment_submissions SET pdf_id=(SELECT last_insert_rowid()) WHERE assignment_no=? AND student_no=?",[request.form["assignment_no"],session["username"]])
                            elif assignmentExists["pdf_id"]:
                                ##Updates pdf file instead
                                insert_db("UPDATE pdf SET pdf_name=?,pdf_data=? WHERE pdf_id=?",[request.files["assignment_pdf"].filename, request.files["assignment_pdf"].read(), assignmentExists["pdf_id"]])
                            ## Checks for late submission and records the time of submission for incremental late penalties if desired
                            if assignment["due_date"]:
                                if datetime.strptime(assignment["due_date"], "%Y-%m-%dT%H:%M:%S.%f") <= now:
                                    insert_db("UPDATE assignment_submissions SET date_submitted=?,late=1 WHERE assignment_no=? AND student_no=?",[now.isoformat(),request.form["assignment_no"],session["username"]])
                                else:
                                    insert_db("UPDATE assignment_submissions SET date_submitted=?,late=0 WHERE assignment_no=? AND student_no=?",[now.isoformat(),request.form["assignment_no"],session["username"]])
                            else:
                                insert_db("UPDATE assignment_submissions SET date_submitted=?,late=0 WHERE assignment_no=? AND student_no=?",[now.isoformat(),request.form["assignment_no"],session["username"]])
                    else:
                        flash("No such assignment")
                ## Test Submission
                elif "test_no" in request.form:
                    test = query_db("SELECT * FROM tests WHERE test_no=?",[request.form["test_no"]],one=True)
                    if test:
                        testExists = query_db("SELECT * FROM test_submissions WHERE student_no=? AND test_no=?",[session["username"], request.form["test_no"]],one=True)
                        if not testExists:
                            insert_db("INSERT INTO test_submissions (test_no,student_no,marked) VALUES (?,?,0)",[request.form["test_no"],session["username"]])
                            testExists = query_db("SELECT * FROM test_submissions WHERE student_no=? AND test_no=?",[session["username"], request.form["test_no"]],one=True)
                        if request.files.get("test_pdf"):
                            if not testExists["pdf_id"]:
                                ## Insert if test does not exist
                                insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["test_pdf"].filename, request.files["test_pdf"].read(), session["username"]])
                                insert_db("UPDATE test_submissions SET pdf_id=(SELECT last_insert_rowid()) WHERE test_no=? AND student_no=?",[request.form["test_no"],session["username"]])
                            elif testExists["pdf_id"]:
                                ## Update pdf file
                                insert_db("UPDATE pdf SET pdf_name=?,pdf_data=? WHERE pdf_id=?",[request.files["test_pdf"].filename, request.files["test_pdf"].read(), testExists["pdf_id"]])
                            ## Checks for late submission and records the time of submission for incremental late penalties if desired
                            if test["due_date"]:
                                if datetime.strptime(test["due_date"], "%Y-%m-%dT%H:%M:%S.%f") <= now:
                                    insert_db("UPDATE test_submissions SET date_submitted=?,late=1 WHERE test_no=? AND student_no=?",[now.isoformat(),request.form["test_no"],session["username"]])
                                else:
                                    insert_db("UPDATE test_submissions SET date_submitted=?,late=0 WHERE test_no=? AND student_no=?",[now.isoformat(),request.form["test_no"],session["username"]])
                            else:
                                insert_db("UPDATE test_submissions SET date_submitted=?,late=0 WHERE test_no=? AND student_no=?",[now.isoformat(),request.form["test_no"],session["username"]])
                    else:
                        flash("Error: no such test")
                ##Regrade Request
                elif "dropmenu" in request.form:
                    if request.form["dropmenu"] == "assignment":
                        assignmentExists = query_db("SELECT * FROM assignment_submissions WHERE assignment_no=? AND student_no=?",[request.form["evaluation_no"],session["username"]],one=True)
                        if assignmentExists:
                            if assignmentExists["marked"]:
                                insert_db("UPDATE assignment_submissions SET regrade_requested=1 WHERE assignment_no=? AND student_no=?",[request.form["evaluation_no"],session["username"]])
                            else:
                                flash("This assignment has yet to be marked")
                        else:
                            flash("No submission detected")
                    elif request.form["dropmenu"] == "test":
                        testExists = query_db("SELECT * FROM test_submissions WHERE student_no=? AND test_no=?",[session["username"], request.form["evaluation_no"]],one=True)
                        if testExists:
                            if testExists["marked"]:
                                insert_db("UPDATE test_submissions SET marked=0, regrade_requested=1 WHERE test_no=? AND student_no=?",[request.form["evaluation_no"],session["username"]])
                            else:
                                flash("This test has yet to be marked")
                        else:
                            flash("No submission detected")
                else:
                    flash("No such post request supported")
                return redirect(url_for("coursework"))
            return render_template("courseWork.html",
                assignments=assignments,
                assignment_submissions=assignment_submissions,
                test_submissions=test_submissions,
                tests=tests,
                student="student")
    return redirect(url_for("login"))

@app.route("/links")
def links():
    if "username" in session :
        return render_template("links.html")
    return redirect(url_for("login"))

@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if "username" in session:
        ##Queries whether there is a username match in instructors table
        qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
        ##Queries whether there is a username match in ta table
        qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
        # user is a student
        if qi[0]["col"] != 1 and qt[0]["col"] != 1:
            instructor = query_db("SELECT instructor.instructor_code, instructor.first_name, instructor.last_name FROM instructor, student WHERE student.student_no=? AND student.instructor_code=instructor.instructor_code", [session["username"]])
            ta = query_db("SELECT ta.ta_code, ta.first_name, ta.last_name FROM ta, student WHERE student.student_no=? AND student.ta_code=ta.ta_code", [session["username"]])
            if request.method == "POST":
                if 'iq1' in request.form and request.form['iq1']:
                    insert_db("INSERT INTO instr_feedback (instructor_code, question_1, question_2, question_3) VALUES (?,?,?,?)", [instructor[0]["instructor_code"], request.form["iq1"], request.form["iq2"], request.form["iq3"]])
                    if request.form['iq4']:
                        insert_db("UPDATE instr_feedback SET question_4=? WHERE feedback_no=(SELECT last_insert_rowid())", [request.form["iq4"]])
                if 'taq1' in request.form and request.form['taq1']:
                    insert_db("INSERT INTO ta_feedback (ta_code, question_1, question_2, question_3) VALUES (?,?,?,?)", [ta[0]["ta_code"], request.form["taq1"], request.form["taq2"], request.form["taq3"]])
                    if request.form['taq4']:
                        insert_db("UPDATE instr_feedback SET question_4=? WHERE feedback_no=(SELECT last_insert_rowid())", [request.form["taq4"]])
                return redirect(url_for("feedback"))
            return render_template("feedback.html",
            instructor=instructor,
            ta=ta)
        else: 
            return "ERROR: you do not have permission to view this page"
    return redirect(url_for("login"))

@app.route("/profile", methods=["GET","POST"])
def profile():
    if "username" in session :
        if id is not None:
            ##Queries whether there is a username match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[session["username"]])
            ##Queries whether there is a username match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=?)) AS \"col\"",[session["username"]])
            # Load Instructor page
            if qi[0]["col"] == 1:
                instructor_info = query_db("SELECT * FROM instructor WHERE instructor_code=?",[session["username"]])
                prof_pic = instructor_info[0]["instructor_picture"]
                if prof_pic != None:
                    prof_pic = base64.b64encode(instructor_info[0]["instructor_picture"]).decode("ascii")
                syllabus = query_db("SELECT * FROM pdf INNER JOIN instructor ON instructor.syllabus_id = pdf.pdf_id AND instructor.instructor_code=?", [session["username"]])
                if request.method == "POST":
                    #update instructor form
                    if 'picture' in request.files and request.files["picture"]: # if picture key is not in the post request
                        pic = request.files["picture"].read()
                        insert_db("UPDATE instructor SET instructor_picture=? WHERE instructor_code=?", [pic, session["username"]])
                    if 'syllabus' in request.files and request.files["syllabus"]:
                        # query db to see if theres is a syllabus
                        fileExists = query_db("SELECT * FROM instructor WHERE instructor_code=?", [session["username"]])
                        if fileExists[0]["syllabus_id"]:
                            sy_id = fileExists[0]["syllabus_id"]
                            insert_db("UPDATE pdf SET pdf_name=?, pdf_data=? WHERE pdf_id=?", [request.files["syllabus"].filename, request.files["syllabus"].read(), sy_id])
                        else:
                            insert_db("INSERT INTO pdf (pdf_name,pdf_data,username) VALUES (?,?,?)",[request.files["syllabus"].filename, request.files["syllabus"].read(), session["username"]])
                            insert_db("UPDATE instructor SET syllabus_id=(SELECT last_insert_rowid()) WHERE instructor_code=?",[session["username"]])
                    if 'first_lecture_time' in request.form and request.form["first_lecture_time"]:
                        insert_db("UPDATE instructor SET first_lecture_time=? WHERE instructor_code=?", [request.form["first_lecture_time"], session["username"]])
                    if 'first_lecture_link' in request.form and request.form["first_lecture_link"]:
                        insert_db("UPDATE instructor SET first_lecture_link=? WHERE instructor_code=?", [request.form["first_lecture_link"], session["username"]])
                    if 'second_lecture_time' in request.form and request.form["second_lecture_time"]:
                        insert_db("UPDATE instructor SET second_lecture_time=? WHERE instructor_code=?", [request.form["second_lecture_time"], session["username"]])
                    if 'second_lecture_link' in request.form and request.form["second_lecture_link"]:
                        insert_db("UPDATE instructor SET second_lecture_link=? WHERE instructor_code=?", [request.form["second_lecture_link"], session["username"]])
                    if 'office' in request.form and request.form["office"]:
                        insert_db("UPDATE instructor SET office=? WHERE instructor_code=?", [request.form["office"], session["username"]])
                    if 'office_hours' in request.form and request.form["office_hours"]:
                        insert_db("UPDATE instructor SET office_hours=? WHERE instructor_code=?", [request.form["office_hours"], session["username"]])
                    if 'office_hours_link' in request.form and request.form["office_hours_link"]:
                        insert_db("UPDATE instructor SET office_hours_link=? WHERE instructor_code=?", [request.form["office_hours_link"], session["username"]])
                    if 'email' in request.form and request.form["email"]:
                        insert_db("UPDATE instructor SET email=? WHERE instructor_code=?", [request.form["email"], session["username"]])
                    if 'password' in request.form and request.form["password"]:
                        insert_db("UPDATE instructor SET password=? WHERE instructor_code=?", [request.form["password"], session["username"]])
                    return redirect(url_for(".profile",id=id))
                return render_template("profile.html", 
                    user_type=0,
                    user_info=instructor_info,
                    pic=prof_pic,
                    syllabus=syllabus)
            # Load TA page
            elif qt[0]["col"] == 1:
                ta_info = query_db("SELECT * FROM ta WHERE ta_code=?",[session["username"]])
                ta_pic = ta_info[0]["ta_picture"]
                if ta_pic != None:
                    ta_pic = base64.b64encode(ta_info[0]["ta_picture"]).decode("ascii")
                if request.method == "POST":
                    #update form info case
                    if 'picture' in request.files and request.files["picture"]: # if picture key is not in the post request
                        pic = request.files["picture"].read()
                        insert_db("UPDATE ta SET ta_picture=? WHERE ta_code=?", [pic, session["username"]])
                    if 'office_hours' in request.form and request.form["office_hours"]:
                        insert_db("UPDATE ta SET office_hours=? WHERE ta_code=?", [request.form["office_hours"], session["username"]])
                    if 'office_hours_link' in request.form and request.form["office_hours_link"]:
                        insert_db("UPDATE ta SET office_hours_link=? WHERE ta_code=?", [request.form["office_hours_link"], session["username"]])
                    if 'email' in request.form and request.form["email"]:
                        insert_db("UPDATE ta SET email=? WHERE ta_code=?", [request.form["email"], session["username"]])
                    if 'password' in request.form and request.form["password"]:
                        insert_db("UPDATE ta SET password=? WHERE ta_code=?", [request.form["password"], session["username"]])
                    return redirect(url_for(".profile",id=id))
                return render_template("profile.html", 
                    user_type=1,
                    user_info=ta_info,
                    pic=ta_pic)
            # Load Student page
            else:
                prof_list = query_db("SELECT instructor_code, first_name, last_name FROM instructor")
                ta_list = query_db("SELECT ta_code, first_name, last_name FROM ta")
                stud_info = query_db("SELECT * FROM student WHERE student_no=?",[session["username"]])
                if request.method == "POST":
                    if 'prof' in request.form and request.form["prof"]:
                        insert_db("UPDATE student SET instructor_code=? WHERE student_no=?", [request.form["prof"], session["username"]])
                    if 'ta' in request.form and request.form["ta"]:
                        insert_db("UPDATE student SET ta_code=? WHERE student_no=?", [request.form["ta"], session["username"]])
                    if 'email' in request.form and request.form["email"]:
                        insert_db("UPDATE student SET email=? WHERE student_no=?", [request.form["email"], session["username"]])
                    if 'password' in request.form and request.form["password"]:
                        insert_db("UPDATE student SET password=? WHERE student_no=?", [request.form["password"], session["username"]])
                    return redirect(url_for(".profile",id=id))
                return render_template("profile.html",
                    user_type=2,
                    user_info=stud_info, 
                    prof_list=prof_list,
                    ta_list=ta_list)    
    return redirect(url_for("login"))

##LOGIN/SIGNUP REQUESTS
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        ## IF REQUEST = LOGIN
        if request.form["firstname"] == "" and request.form["lastname"] == "":
            ##Queries whether there is a username and password match in instructors table
            qi = query_db("SELECT EXISTS(SELECT instructor_code,password FROM instructor WHERE (instructor_code=? AND password=?)) AS \"col\"",[request.form["username"],request.form["password"]])
            ##Queries whether there is a username and password match in ta table
            qt = query_db("SELECT EXISTS(SELECT ta_code,password FROM ta WHERE (ta_code=? AND password=?)) AS \"col\"",[request.form["username"],request.form["password"]])
            ##Queries whether there is a username and password match in student table
            qs = query_db("SELECT EXISTS(SELECT student_no,password FROM student WHERE (student_no=? AND password=?)) AS \"col\"",[request.form["username"],request.form["password"]])
            t = qi[0]["col"] + qt[0]["col"] + qs[0]["col"]
            if t==0:
                error = "Invalid credentials"
            elif t==1:
                session["username"] = request.form["username"]
                return redirect(url_for("home"))
        ##else: register the user then add the user to session and redirect them to home route and handle duplicate username error/ 
        else:
            ##Queries whether username exists already or not
            qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[request.form["username"]])
            qt = query_db("SELECT EXISTS(SELECT ta_code FROM ta WHERE (ta_code=?)) AS \"col\"",[request.form["username"]])
            qs = query_db("SELECT EXISTS(SELECT student_no FROM student WHERE (student_no=?)) AS \"col\"",[request.form["username"]])
            t = 0
            t = qi[0]["col"] + qt[0]["col"] + qs[0]["col"]
            if t >= 1:
                ##ERROR: user exits 
                error="User already exists"
            elif t == 0:
                ##USER DOES NOT EXIST SO DETERMINE THE USER LEVEL AND CREATE THE RESPECTIVE USER ENTRY
                if request.form["creationcode"] == "0" and request.form["InstructorsCode"]:
                    qi = query_db("SELECT EXISTS(SELECT instructor_code FROM instructor WHERE (instructor_code=?)) AS \"col\"",[request.form["InstructorsCode"]])
                    if (qi[0]["col"] == 1):
                        insert_db("INSERT INTO student (student_no ,first_name ,last_name ,email ,password,instructor_code) VALUES (?,?,?,?,?,?)",
                        [request.form["username"],request.form["firstname"],request.form["lastname"],request.form["email"],request.form["password"],request.form["InstructorsCode"]])
                        session["username"] = request.form["username"]
                        return redirect(url_for("home"))
                    else:
                        error="Invalid instructor code"
                elif request.form["creationcode"] =="1" and not request.form["InstructorsCode"]:
                    insert_db("INSERT INTO instructor (instructor_code, first_name, last_name, email, password) VALUES (?,?,?,?,?)",
                        [request.form["username"],request.form["firstname"],request.form["lastname"],request.form["email"],request.form["password"]])
                    session["username"] = request.form["username"]
                    return redirect(url_for("home"))
                elif request.form["creationcode"] == "2" and not request.form["InstructorsCode"]:
                    insert_db("INSERT INTO ta (ta_code,first_name ,last_name ,email ,password) VALUES (?,?,?,?,?)",
                        [request.form["username"],request.form["firstname"],request.form["lastname"],request.form["email"],request.form["password"]])
                    session["username"] = request.form["username"]
                    return redirect(url_for("home"))
                else:
                    error="invalid user type"
    return render_template("login.html", error=error)

##LOGOUT REQUESTS
@app.route("/logout")
def logout():
   ## Removes the username from the session if it exists
   session.pop("username", None)
   return redirect(url_for("login"))
    
if __name__ == "__main__":
    app.run(debug=True)