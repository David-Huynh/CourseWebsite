import os
from flask import Flask, render_template, session, url_for, redirect, request
app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')

app.secret_key = "5siXpv0D_-iyU{?/DMX~"

@app.route('/')
def home():
    if 'username' in session:
        return render_template("index.html")
    return redirect(url_for('login'))
@app.route('/lectures')
def lectures():
    return render_template("lectures.html")

@app.route('/coursework')
def coursework():
    return render_template("courseWork.html")

@app.route('/links')
def links():
    return render_template("links.html")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST': 
        session['username'] = request.form['username']
        return redirect(url_for('index'))
    return '''
        <form method="post">
            <p><input type=text name=username>
            <p><input type=submit value=Login>
        </form>
    '''
if __name__ == "__main__":
    app.run(debug=True)