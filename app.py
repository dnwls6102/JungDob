from pymongo import MongoClient, ReturnDocument
from flask import Flask, render_template, jsonify, request
from datetime import datetime
from operator import itemgetter

app = Flask(__name__)

client = MongoClient('mongodb://root:root@13.125.162.42', 27017)
db = client.jungdob

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/signin')
def signin():
    return render_template("signin.html")

@app.route('/writeQ')
def writeQ():
    return render_template("writeQ.html")

@app.route('/post')
def post():
    return render_template("post.html")

@app.route('/main')
def main():
    return render_template("main.html")


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

@app.route('/api/getUserimage', methods=['GET'])
def getUserimage():
    user_id = request.form['user_id']
    user = db.user.find_one({"id":user_id})
    picture = open('./static/user_picture/' + user['id'] + '.jpg')
    return jsonify({'result': 'success', 'file': picture})


@app.route('/api/signIn', methods=['GET'])
def signIn():
    print("hello world")
    return jsonify({'result': 'success'})

@app.route('/api/signUp', methods=['POST']) #
def signUp():
    print("signUp")
    user = request.get_json()
    #image = request.file['image']
    user["id"] = getNextSequence("user")
    #extension = image.filename.split('.')[1]
    #user['image'] = user['id'] + '.' + extension
    print(user)
    db.user.insert_one(user)
    #image.save('./static/user_iamge/' + user['image'])
    return jsonify({'result': 'success'})

@app.route('/api/checkIDUsed', methods=['POST']) #
def checkIDUsed():
    print("checkIDUsed")
    temp_id = request.get_json()["account_id"]
    print(temp_id)
    is_id_used = len(list(db.user.find({'account_id':temp_id})))
    print(is_id_used)
    if is_id_used > 0:
        ret = True
    elif is_id_used == 0:
        ret = False
    return jsonify({'result': 'success', 'isUsed': ret})
    #return "success"


@app.route('/api/getPostList', methods=['POST']) #
def getPostList():
    week = request.get_json()['week']
    print(week)
    sorting_method = request.get_json()['sorting_method']
    if sorting_method == "time":
        #ret = list(db.post.find({"week": week}))
        ret = sorted(list(db.post.find({"week": week})), key=itemgetter('time'), reverse=True)
    elif sorting_method == "like":
        ret = sorted(list(db.post.find({"week": week})), key=itemgetter('like_num'), reverse=True)
    for _post in ret:
        _post.pop('_id')
    print(ret)
    return jsonify({'result': 'success', 'post': ret})

# my page post list
#user_id = request.form['user_id']
#week = request.form['week']
#sorting_method = request.form['sorting_method']
#if sorting_method == "time":
#    ret = db.post.find({"$and": [{"author_id":user_id}, {"week", week}]}).sort({"time":-1})
#elif sorting_method == "like":
#    ret = db.post.find({"$and": [{"author_id":user_id}, {"week", week}]}).sort({"like_num":-1})
#return jsonify({'result': 'success'}, {'list': ret})


@app.route('/api/createPost', methods=['POST']) #
def createPost():
    post = request.get_json()
    post["id"] = getNextSequence("post")
    post['like_num'] = 0
    post['like_user_id_list'] = []
    post['solved_comment_id'] = -1
    post['comment_id_list'] = []
    post['time'] = datetime.now().strftime("%Y %m %d %H %M %S %f")
    print(post)
    db.post.insert_one(post)
    return jsonify({'result': 'success'})


@app.route('/api/getCurrentPost', methods=['GET'])
def getCurrentPost():
    post_id = request.form['post_id']
    post = db.post.find_one({"id":post_id})
    return jsonify({'result': 'success', "post": post})

@app.route('/api/getCommentList', methods=['GET'])
def getCommentList():
    post_id = request.form['post_id']
    post = db.post.find_one({"id":post_id})
    comment_id_list = post['like_user_id_list']
    comment_list = []
    for id in comment_id_list:
        comment_list.append(db.post.find_one({'id':id}))
    return jsonify({'result': 'success', 'comments':comment_list})

@app.route('/api/deletePost', methods=['DELETE'])
def deletePost():
    post_id = request.form['post_id']
    user_id = request.form['user_id']
    post = db.post.find_one({"id":post_id})
    if post['author_id'] != user_id:
        return jsonify({'result': 'false'})
    else:
        comment_id_list = post['like_user_id_list']
        for id in comment_id_list:
            db.comment.delete_one({'id': id})
        db.post.delete_one({"id":post_id})
        return jsonify({'result': 'success'})

@app.route('/api/createComment', methods=['POST'])
def createComment():
    comment = request.get_json()
    post_id = comment['post_id']
    comment.pop('post_id')
    comment["id"] = getNextSequence("comment")
    comment['like_user_id_list'] = []
    comment['hate_user_id_list'] = []
    comment['time'] = datetime.now()
    db.comment.insert_one(comment)

    post = db.post.find_one({"id":post_id})
    post['comment_id_list'].append(comment["id"])
    db.post.delete_one({"id":post_id})
    db.post.insert_one(post)
    return jsonify({'result': 'success'})

@app.route('/api/deleteComment', methods=['DELETE'])
def deleteComment():
    user_id = request.form['user_id']
    comment_id = request.form['comment_id']
    comment = db.comment.find_one({"id":comment_id})
    if comment['author_id'] != user_id:
        return jsonify({'result': 'false'})
    else:
        db.comment.delete_one({'id': comment_id})
        post_id = comment['post_id']
        post = db.post.find_one({"id":post_id})
        post['comment_id_list'].remove(comment_id)
        db.post.delete_one({"id":post_id})
        db.post.insert_one(post)
        return jsonify({'result': 'success'})
    
@app.route('/api/pressPostLike', methods=['POST'])
def pressPostLike():
    post_id = request.form['post_id']
    account_id = request.form['account_id']
    post = db.post.find_one({"id":post_id})
    if account_id not in post['like_user_id_list']:
        post['like_user_id_list'].append(account_id)
        post['like_num'] += 1
    else:
        post['like_user_id_list'].remove(account_id)
        post['like_num'] -= 1
    db.post.delete_one({"id":post_id})
    db.post.insert_one(post)
    return jsonify({'result': 'success'})

@app.route('/api/pressCommentLike', methods=['POST'])
def pressCommentLike():
    comment_id = request.form['comment_id']
    account_id = request.form['account_id']
    comment = db.comment.find_one({"id":comment_id})
    if account_id not in comment['like_user_id_list'] and account_id not in comment['hate_user_id_list']:
        comment['like_user_id_list'].append(account_id)
    elif account_id in comment['like_user_id_list'] and account_id not in comment['hate_user_id_list']:
        comment['like_user_id_list'].remove(account_id)
    elif account_id not in comment['like_user_id_list'] and account_id in comment['hate_user_id_list']:
        comment['like_user_id_list'].append(account_id)
        comment['hate_user_id_list'].remove(account_id)
    return jsonify({'result': 'success'})

@app.route('/api/pressCommentHate', methods=['POST'])
def pressCommentHate():
    comment_id = request.form['comment_id']
    account_id = request.form['account_id']
    comment = db.comment.find_one({"id":comment_id})
    if account_id not in comment['like_user_id_list'] and account_id not in comment['hate_user_id_list']:
        comment['hate_user_id_list'].append(account_id)
    elif account_id in comment['like_user_id_list'] and account_id not in comment['hate_user_id_list']:
        comment['hate_user_id_list'].remove(account_id)
    elif account_id not in comment['like_user_id_list'] and account_id in comment['hate_user_id_list']:
        comment['hate_user_id_list'].append(account_id)
        comment['like_user_id_list'].remove(account_id)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.run('0.0.0.0', port=5050, debug=True)