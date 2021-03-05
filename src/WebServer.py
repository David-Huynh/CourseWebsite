from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")
@app.route('/assignments')
def assignments():
    return render_template("assignments.html")
@app.route('/syllabus')
def syllabus():
    return render_template("syllabus.html")

if __name__ == "__main__":
    app.run(debug=True)