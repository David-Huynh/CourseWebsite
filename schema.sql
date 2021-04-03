CREATE TABLE pdf(
	pdf_id INTEGER NOT NULL UNIQUE,
	pdf_name TEXT NOT NULL,
	pdf_data BLOB NOT NULL,
	username TEXT,
	PRIMARY KEY(pdf_id AUTOINCREMENT)
);
CREATE TABLE instructor(
	instructor_code TEXT NOT NULL UNIQUE,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL,
	password TEXT NOT NULL,
	
	
	first_lecture_link TEXT,
	second_lecture_link TEXT,
	first_lecture_time TEXT,
	second_lecture_time TEXT,
	
	office TEXT,
	office_hours TEXT,
	tutorial_hours TEXT,
	office_hours_link TEXT,
	tutorial_link TEXT,
	
	syllabus_id TEXT,
	instructor_picture BLOB,
	PRIMARY KEY (instructor_code),
	FOREIGN KEY (syllabus_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE instr_feedback (
	feedback_no INTEGER NOT NULL,
	instructor_code TEXT NOT NULL,
	question_1 TEXT,
	question_2 TEXT,
	question_3 TEXT,
	question_4 TEXT,
	PRIMARY KEY(feedback_no, instructor_code),
	FOREIGN KEY(instructor_code) REFERENCES instructor(instructor_code)
);

CREATE TABLE instr_notes (
	week INTEGER NOT NULL,
	instructor_code TEXT NOT NULL,
	pdf_id INT NOT NULL,
	PRIMARY KEY(week, instructor_code, pdf_id),
	FOREIGN KEY(instructor_code) REFERENCES instructor(instructor_code),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE lec_pdfs (
	week INTEGER NOT NULL,
	pdf_id INT NOT NULL,
	PRIMARY KEY (week, pdf_id),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE lectures(
	week INTEGER NOT NULL,
	lecture_title TEXT NOT NULL,
	instructor_code TEXT NOT NULL,
	tues_recording TEXT,
	thurs_recording TEXT,
	PRIMARY KEY (week, instructor_code),
	FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code)
);
CREATE TABLE ta(
	ta_code TEXT NOT NULL UNIQUE,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL,
	password TEXT NOT NULL,
	
	office_hours TEXT,
	tutorial_hours TEXT,
	office_hours_link TEXT,
	tutorial_link TEXT,
	ta_picture BLOB,
	PRIMARY KEY (ta_code)
);

CREATE TABLE ta_feedback (
	feedback_no INTEGER NOT NULL,
	ta_code TEXT NOT NULL,
	question_1 TEXT,
	question_2 TEXT,
	question_3 TEXT,
	question_4 TEXT,
	PRIMARY KEY(feedback_no, ta_code),
	FOREIGN KEY(ta_code) REFERENCES ta(ta_code)
);

CREATE TABLE ta_notes (
	week INTEGER NOT NULL,
	ta_code TEXT NOT NULL,
	pdf_id INTEGER NOT NULL,
	PRIMARY KEY(week, ta_code, pdf_id),
	FOREIGN KEY(ta_code) REFERENCES ta(ta_code),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE tut_pdfs (
	week INTEGER NOT NULL,
	pdf_id INTEGER NOT NULL,
	PRIMARY KEY (week, pdf_id),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE tutorials(
	week INTEGER NOT NULL,
	ta_code TEXT NOT NULL,
	recording_link TEXT,
	PRIMARY KEY (week, ta_code),
	FOREIGN KEY (ta_code) REFERENCES ta(ta_code)
);

CREATE TABLE student (
	student_no TEXT NOT NULL UNIQUE,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL,
	password TEXT NOT NULL,
	
	ta_code TEXT,
	instructor_code TEXT NOT NULL,
	PRIMARY KEY (student_no),
	FOREIGN KEY (ta_code) REFERENCES ta(ta_code),
	FOREIGN KEY (instructor_code) REFERENCES instructor(instructor_code)
);

CREATE TABLE assignments (
	assignment_no INTEGER NOT NULL UNIQUE,
	pdf_id INTEGER,
	solution_id INTEGER,
	due_date TEXT,
	PRIMARY KEY (assignment_no),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id),
	FOREIGN KEY (solution_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE assignment_submissions (
	assignment_no INTEGER NOT NULL,
	student_no TEXT NOT NULL,
	pdf_id INTEGER,
	grade REAL,
	date_submitted TEXT,
	late INTEGER,
	marked INTEGER NOT NULL,
	regrade_requested INTEGER,
	PRIMARY KEY (assignment_no, student_no),
	FOREIGN KEY (assignment_no) REFERENCES assignments(assignment_no),
	FOREIGN KEY (student_no) REFERENCES student(student_no),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id)
);
CREATE TABLE tests (
	test_no INTEGER NOT NULL UNIQUE,
	pdf_id INTEGER,
	solution_id INTEGER,
	due_date TEXT,
	PRIMARY KEY (test_no),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id),
	FOREIGN KEY (solution_id) REFERENCES pdf(pdf_id)
);

CREATE TABLE test_submissions (
	test_no INTEGER NOT NULL,
	student_no TEXT NOT NULL,
	pdf_id INTEGER,
	grade REAL,
	date_submitted TEXT,
	late INTEGER,
	marked INTEGER NOT NULL,
	regrade_requested INTEGER,
	PRIMARY KEY (test_no, student_no),
	FOREIGN KEY (test_no) REFERENCES tests(test_no),
	FOREIGN KEY (student_no) REFERENCES student(student_no),
	FOREIGN KEY (pdf_id) REFERENCES pdf(pdf_id)
);