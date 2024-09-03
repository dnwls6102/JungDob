from pymongo import MongoClient
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
db = client.jungdob



@app.route('/')
def index():
    return render_template("index.html")

@app.route('/login')
def login():
    return render_template("login.html")

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

#sadsada