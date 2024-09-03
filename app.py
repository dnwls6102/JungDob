from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/signin')
def signin():
    return render_template("signin.html")

@app.route('/writeQ')
def writeQ():
    return render_template("writeQ.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)

#sadsada