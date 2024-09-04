from pymongo import MongoClient, ReturnDocument
from flask import Flask, render_template, jsonify, request, redirect, url_for, session
from flask_jwt_extended import *
from datetime import datetime
from operator import itemgetter

import re

app = Flask(__name__)

client = MongoClient('mongodb://root:root@13.125.162.42', 27017)
#client = MongoClient('localhost', 27017)
db = client.jungdob

jwt = JWTManager(app)

#@app.route('/')
#@jwt_required(optional=True)
#def index():
#    cur_user = get_jwt_identity()
#    print(cur_user)
#    if not cur_user:
#        return render_template("index.html")
#    else:
#        return render_template("main.html")

@app.route('/')
def index():
    return render_template("index.html")

#    cur_user = get_jwt_identity()
#    if not cur_user:
#        return redirect(url_for('main'))
#    else:
#        return render_template("index.html")

@app.route('/signin')
def signin():
    return render_template("signin.html")

@app.route('/writeQ')
def writeQ():
    return render_template("writeQ.html")

@app.route('/post', methods=['GET'])
def post():
    id_receive = request.args.get('id')
    print(id_receive)
    post = list(db.post.find({'id' : int(id_receive)}))
    post = post[0]
    authorInfo = list(db.user.find({'id' : post['author_id']}))[0]
    userdb = list(db.user.find({}))
    reply_db = []
    reply_users_db = []
    for i in post['comment_id_list']:
        for x in list(db.comment.find({})):
            like_num = 0
            hate_num = 0
            print(x)
            if x['id'] == i :
                for t in x['like_user_id_list']:
                    like_num += 1
                for h in x['hate_user_id_list']:
                    hate_num += 1
                x['like_num'] = like_num
                x['hate_num'] = hate_num
                reply_db.append(x)
        for u in userdb :
            if u['id'] == i :
                reply_users_db.append(u)
    temp_reply_num = 0
    print(reply_users_db)
    for i in post['comment_id_list']:
        temp_reply_num += 1
    
    return render_template("post.html", post = post, authorInfo = authorInfo, reply_num = temp_reply_num,
                           reply_db = reply_db, reply_users_db = reply_users_db)

@app.route('/main')
def main():
    ret = sorted(list(db.post.find({})), key=itemgetter('time'), reverse=True)
    users = list(db.user.find({}))
    for _post in ret:
        _post.pop('_id')
    for x in ret:
        temp_reply_num = 0
        print(x)
        for z in x['comment_id_list'] :
            temp_reply_num += 1
        x['reply_num'] = temp_reply_num
    return render_template("main.html", posts = ret, users = users, name = 'Null')


# API
def getNextSequence(collection):
    temp = db.counter.find_one_and_update({'_id':collection}, 
        {'$inc': {"seq":1}}, return_document=ReturnDocument.AFTER)
    return temp["seq"]

@app.route('/api/getUserInfo', methods=['POST'])
def getUserInfo():
    user_id = request.form['user_id']
    user = db.user.find_one({'id':int(user_id)})
    user.pop("_id")
    return jsonify({'result': 'success', "user":user})

@app.route('/api/getUserimage', methods=['GET'])
def getUserimage():
    user_id = request.form['user_id']
    user = db.user.find_one({"id":user_id})
    picture = open('./static/user_picture/' + user['id'] + '.jpg')
    return jsonify({'result': 'success', 'file': picture})

   

    result = list(db.user.find({'account_id' : id_receive , 'account_pw' : pw_receive}))
    if len(result) == 0:
        return jsonify({'result' : 'noMatch'})
    else :
        return jsonify({'result' : 'success'})
    return jsonify({'result': 'fail'})

#@app.route('/api/signIn', methods = ['POST'])
#def idCheck():
#    if request.method == "POST":
#        print("받아옴")
#        id_receive = request.form['user_id']
#        print(id_receive)
#        result = list(db.user.find({'account_id' : id_receive}))
#        print(result)
#        if len(result) == 0:
#            return jsonify({'result' : 'success'})
#        else :
#            return jsonify({'result' : 'noMatch'})

@app.route('/api/signIn', methods=['POST'])
def signIn2():
    account_id = request.form['account_id']
    account_pw = request.form['account_pw']
    account = db.user.find_one({'account_id':account_id})
    user_id = account["id"]
    if account != None and account['account_pw'] == account_pw:
        access_token = create_access_token(identity = user_id)
        return jsonify({'result': 'success', "access_token":access_token})
    else:
        return jsonify({'result': 'fail'})

@app.route('/api/signOut', methods=['GET'])
def signOut():
    response = jsonify({'result': 'success'})
    unset_jwt_cookies(response)
    return response


@app.route('/api/signUp', methods=['POST']) #
def signUp():
    print("signUp")
    
    account_id= request.form['account_id']
    account_pw = request.form['account_pw']
    user_name=request.form['user_name']
    account_class= request.form['jungle_class']
    slack_id= request.form['slack_id']
    user_mbti= request.form['user_MBTI']
    picture=request.form['picture']
    
    user ={
        'account_id': account_id, 'account_pw' : account_pw,
        'user_name':user_name,'MBTI':user_mbti,
        'jungle_class':account_class,
        'slack_id':slack_id,
        'picture':picture
    }
    user["id"] = getNextSequence("user")
    db.user.insert_one(user)

    # user = request.get_json()
    #image = request.file['image']

    #extension = image.filename.split('.')[1]
    #user['image'] = user['id'] + '.' + extension
    print(user)
    

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
    week = int(request.form['week'])
    sorting_method = request.form['sorting_method']
    print(week)
    print(db.post.find_one({"week": week}))
    if sorting_method == "time":
        ret = sorted(list(db.post.find({"week": week})), key=itemgetter('time'), reverse=True)
    elif sorting_method == "like":
        ret = sorted(list(db.post.find({"week": week})), key=itemgetter('like_num'), reverse=True)
    for _post in ret:
        _post.pop('_id')
    return jsonify({'result': 'success', 'post': ret})

@app.route('/api/getCompletePostList', methods=['POST']) #
def getCompletePostList():
    week = int(request.form['week'])
    sorting_method = request.form['sorting_method']
    print(week)
    print(db.post.find_one({"week": week}))
    if sorting_method == "time":
        ret = sorted(list(db.post.find({"week": week})), key=itemgetter('time'), reverse=True)
    elif sorting_method == "like":
        ret = sorted(list(db.post.find({"week": week})), key=itemgetter('like_num'), reverse=True)
    in_progress = []
    complete = []
    for _post in ret:
        _post.pop('_id')
        if int(_post["solved_comment_id"]) == -1:
            in_progress.append(_post)
        else:
            complete.append(_post)
    return jsonify({'result': 'success', 'in_progress': in_progress, 'complete':complete})

# my page post list
#user_id = request.form['user_id']
#week = request.form['week']
#sorting_method = request.form['sorting_method']
#if sorting_method == "time":
#    ret = db.post.find({"$and": [{"author_id":user_id}, {"week", week}]}).sort({"time":-1})
#elif sorting_method == "like":
#    ret = db.post.find({"$and": [{"author_id":user_id}, {"week", week}]}).sort({"like_num":-1})
#return jsonify({'result': 'success'}, {'list': ret})

@app.route('/api/select', methods = ["POST"])
#@jwt_required()
def select():
    id = request.form['post_id']
    print(id)
    reply_id = request.form['reply_id']
    print(reply_id)
    print(type(reply_id))
    filter = {'id' : int(id)}
    newvalues = {"$set": {"solved_comment_id"}}
    temp_num = len(list(db.post.find({})))
    db.post.update_one({'id' : int(id)}, {"$set" : {"solved_comment_id" : int(reply_id)}})
    if temp_num != len(list(db.post.find({}))):
        return jsonify({'result' : 'success'})
    else :
        return jsonify({'result' : 'fail'})

@app.route('/api/createPost', methods=['POST']) #
def createPost():
    print("눌러짐")
    #줄바꿈 문자를 <br>로 바꾸기
    post = dict()
    tempweek = re.sub(r'[^0-9]', '', request.form['week'])
    print("변환됨")
    if tempweek == '' :
        print("기타")
        post['week'] = -1
    else :
        print("숫자")
        post['week'] = int(tempweek)
    if request.form['title'] == '':
        print("제목없음")
        return jsonify({'result' : 'noTitle'})
    if request.form['content'] == '':
        print("내용없음")
        return jsonify({'result' : 'noContent'})

    post['title'] = request.form['title']
    post['content'] = request.form['content']
    #post["author_id"] = get_jwt_identity()
    post["author_id"] = 2
    post["id"] = getNextSequence("post")
    post['like_num'] = 0
    post['like_user_id_list'] = []
    post['solved_comment_id'] = -1
    post['comment_id_list'] = []
    post['time'] = datetime.now().strftime("%Y %m %d %H %M %S %f")
    print(post)
    tempnum = len(list(db.post.find()))
    db.post.insert_one(post)
    if tempnum != len(list(db.post.find())) :
         return jsonify({'result': 'success'})
    else :
        return jsonify({'result' : 'fali'})


@app.route('/api/getCurrentPost', methods=['POST']) #
def getCurrentPost():
    post_id = request.get_json()['post_id']
    post = db.post.find_one({"id":post_id})
    post.pop('_id')
    return jsonify({'result': 'success', "post": post})

@app.route('/api/getCommentList', methods=['POST']) #
def getCommentList():
    post_id = request.get_json()['post_id']
    post = db.post.find_one({"id":post_id})
    comment_id_list = post['comment_id_list']
    comment_list = []
    for id in comment_id_list:
        temp = db.comment.find_one({'id':id})
        temp.pop('_id')
        comment_list.append(temp)
    return jsonify({'result': 'success', 'comments':comment_list})

# input {int post_id, int comment_id}
@app.route('/api/solveProblem', methods=['POST'])
def solveProblem():
    post_id = int(request.form['post_id'])
    comment_id = request.form['comment_id']
    post = db.post.find({"id":post_id})
    post["solved_comment_id"] = comment_id
    db.post.delete_one({"id":post_id})
    db.post.insert_one(post)
    return jsonify({'result': 'success'})

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

@app.route('/api/createComment', methods=['POST']) #
def createComment():
    comment = request.get_json()
    post_id = comment['post_id']
    comment.pop('post_id')
    comment["id"] = getNextSequence("comment")
    comment['like_user_id_list'] = []
    comment['hate_user_id_list'] = []
    comment['time'] = datetime.now().strftime("%Y %m %d %H %M %S %f")
    db.comment.insert_one(comment)

    post = db.post.find_one({"id":post_id})
    post['comment_id_list'].append(comment["id"])
    db.post.delete_one({"id":post_id})
    db.post.insert_one(post)
    return jsonify({'result': 'success'})

@app.route('/api/deleteComment', methods=['DELETE'])
def deleteComment():
    user_id = request.get_json()['user_id']
    comment_id = request.get_json()['comment_id']
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
    
@app.route('/api/pressPostLike', methods=['POST']) #
@jwt_required()
def pressPostLike():
    post_id = request.get_json()['post_id']
    account_id = get_jwt_identity()
    post = db.post.find_one({"id":post_id})
    user_id = db.user.find_one({"account_id":account_id})["id"]

    print(post)
    if user_id not in post['like_user_id_list']:
        post['like_user_id_list'].append(user_id)
        post['like_num'] += 1
    else:
        post['like_user_id_list'].remove(user_id)
        post['like_num'] -= 1
    db.post.delete_one({"id":post_id})
    db.post.insert_one(post)
    return jsonify({'result': 'success'})

@app.route('/api/pressCommentLike', methods=['POST']) #
@jwt_required()
def pressCommentLike():
    comment_id = request.get_json()['comment_id']
    account_id = get_jwt_identity()
    comment = db.comment.find_one({"id":comment_id})
    user_id = db.user.find_one({"account_id":account_id})["id"]
    if user_id not in comment['like_user_id_list'] and user_id not in comment['hate_user_id_list']:
        comment['like_user_id_list'].append(user_id)
    elif user_id in comment['like_user_id_list'] and user_id not in comment['hate_user_id_list']:
        comment['like_user_id_list'].remove(user_id)
    elif user_id not in comment['like_user_id_list'] and user_id in comment['hate_user_id_list']:
        comment['like_user_id_list'].append(user_id)
        comment['hate_user_id_list'].remove(user_id)
    db.comment.delete_one({"id":comment_id})
    db.comment.insert_one(comment)
    return jsonify({'result': 'success'})

@app.route('/api/pressCommentHate', methods=['POST']) #
@jwt_required()
def pressCommentHate():
    comment_id = request.get_json()['comment_id']
    account_id = get_jwt_identity()
    comment = db.comment.find_one({"id":comment_id})
    user_id = db.user.find_one({"account_id":account_id})["id"]
    if user_id not in comment['like_user_id_list'] and user_id not in comment['hate_user_id_list']:
        comment['hate_user_id_list'].append(user_id)
    elif user_id not in comment['like_user_id_list'] and user_id in comment['hate_user_id_list']:
        comment['hate_user_id_list'].remove(user_id)
    elif user_id in comment['like_user_id_list'] and user_id not in comment['hate_user_id_list']:
        comment['hate_user_id_list'].append(user_id)
        comment['like_user_id_list'].remove(user_id)
    db.comment.delete_one({"id":comment_id})
    db.comment.insert_one(comment)
    return jsonify({'result': 'success'})

if __name__ == '__main__':
    app.config.update(
        DEBUG = True,
        JWT_SECRET_KEY = "secret key"
    )
    app.run('0.0.0.0', port=5050, debug=True)