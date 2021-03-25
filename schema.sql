CREATE TABLE instructor(
	instructor_code TEXT NOT NULL UNIQUE,
	first_name TEXT NOT NULL,
	last_name TEXT NOT NULL,
	email TEXT NOT NULL,
	password TEXT NOT NULL,
	office_hours TEXT,
	tutorial_hours TEXT,
	office_hours_link TEXT,
	tutorial_link TEXT,
	PRIMARY KEY (instructor_code)
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
	pdf_no INTEGER NOT NULL,
	pdf BLOB,
	PRIMARY KEY(week, instructor_code, pdf_no),
	FOREIGN KEY(instructor_code) REFERENCES instructor(instructor_code)
);

CREATE TABLE lec_pdfs (
	week INTEGER NOT NULL,
	pdf_no INTEGER NOT NULL,
	pdf BLOB,
	PRIMARY KEY (week, pdf_no)
);

CREATE TABLE lectures(
	week INTEGER NOT NULL,
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
	pdf_no INTEGER NOT NULL,
	pdf BLOB,
	PRIMARY KEY(week, ta_code, pdf_no),
	FOREIGN KEY(ta_code) REFERENCES ta(ta_code)
);

CREATE TABLE tut_pdfs (
	week INTEGER NOT NULL,
	pdf_no INTEGER NOT NULL,
	pdf BLOB,
	PRIMARY KEY (week, pdf_no)
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
	pdf BLOB,
	PRIMARY KEY (assignment_no AUTOINCREMENT)
);

CREATE TABLE submissions (
	assignment_no INTEGER NOT NULL,
	student_no TEXT NOT NULL,
	pdf_submission BLOB,
	grade REAL,
	marked INTEGER NOT NULL,
	regrade_requested INTEGER NOT NULL,
	PRIMARY KEY (assignment_no, student_no),
	FOREIGN KEY (assignment_no) REFERENCES assignments(assignment_no),
	FOREIGN KEY (student_no) REFERENCES student(student_no)
);