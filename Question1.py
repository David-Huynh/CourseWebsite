from flask import Flask, render_template
app = Flask(__name__)

@app.route('/<username>')
def generateResponse(username):
    digitFree = ''
    for char in username:
        if not char.isdigit():
            digitFree += char
    return 'Welcome, %s, to my CSCB20 website!' % digitFree

if __name__ == "__main__":
    app.run(debug=True)