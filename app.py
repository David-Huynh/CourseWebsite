from flask import Flask, render_template, session, url_for, redirect, request, flash
app = Flask(__name__, template_folder='./src/templates', static_folder='./src/static')

app.secret_key = "b'\x1a\xe3$e=(\xdc$\xf6\x95}\x00z\x1c\xae\xc2\n\x1a\x08\x85\x1f#9M\xff\xef=x\rg\x9c\xc9'"

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST': 
        if request.form['username'] != 'admin' or request.form['password'] != 'secret':
            error = 'Invalid credentials'
        else:
            session['username'] = request.form['username']
            return render_template("index.html")
    return render_template('login.html', error=error)
    
if __name__ == "__main__":
    app.run(debug=True)