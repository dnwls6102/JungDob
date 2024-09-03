from pymongo import MongoClient, ReturnDocument
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)

client = MongoClient('localhost', 27017)
db = client.jungdob

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

# API
def getNextSequence(collection):
    temp = db.counter.find_one_and_update({'_id':collection}, 
        {'$inc': {"seq":1}}, return_document=ReturnDocument.AFTER)
    return temp["seq"]

@app.route('/api/getUserInfo', methods=['GET'])
def getUserInfo():
    user_id = request.form['user_id']
    user = db.user.find_one({'id':user_id},{
        'id':False,
        'account_id':True,
        'account_pw':False,
        'user_name':True,
        'MBTI':False,
        'jungle_class':False,
        'picture':True,
        'slack_id':True
    })
    return jsonify({'result': 'success'}, user)


@app.route('/api/signIn', methods=['GET'])
def signIn():
    return jsonify({'result': 'success'})


@app.route('/api/signUp', methods=['POST'])
def signUp():
    user = request.get_json()
    user["id"] = getNextSequence("user")
    db.user.insert_one(user)
    return jsonify({'result': 'success'})

@app.route('/api/checkIDUsed', methods=['GET'])
def checkIDUsed():
    temp_id = request.form['account_id']
    temp_cursor = db.user.find_one({'account_id':temp_id})
    is_id_used = temp_cursor.count()
    if is_id_used > 0:
        ret = True
    elif is_id_used == 0:
        ret = False
    return jsonify({'result': 'success'}, {'isUsed': ret})

@app.route('/api/getPostList', methods=['GET'])
def getPostList():
    user_id = request.form['user_id']
    week = request.form['week']
    sorting_method = request.form['sorting_method']
    if sorting_method == "time":
        ret = db.post.find({"$and": [{"author_id":user_id}, {"week", week}]}).sort({"time":-1})
    elif sorting_method == "like":
        ret = db.post.find({"$and": [{"author_id":user_id}, {"week", week}]}).sort({"like_num":-1})
    return jsonify({'result': 'success'}, {'list': ret})


@app.route('/api/createPost', methods=['POST'])
def createPost():
    post = request.get_json()
    post["id"] = getNextSequence("post")
    db.post.insert_one(post)
    return jsonify({'result': 'success'})


@app.route('/api/getCurrentPost', methods=['GET'])
def getCurrentPost():
    post_id = request.form['post_id']
    post = db.post.find_one({"id":post_id})
    return jsonify({'result': 'success'}, post)

@app.route('/api/getCommentList', methods=['GET'])
def getCommentList():
    
    return jsonify({'result': 'success'})

@app.route('/api/deletePost', methods=['DELETE'])
def deletePost():
    return jsonify({'result': 'success'})

@app.route('/api/createComment', methods=['POST'])
def createComment():
    return jsonify({'result': 'success'})

@app.route('/api/deleteComment', methods=['DELETE'])
def deleteComment():
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)