import xlrd
import pandas as pd
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, json
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from sqlalchemy import or_, and_, not_, ForeignKey
from flask_cors import *
import pymysql
import os
import numpy as np
from RecommendMovie import *
from RecommendMovie import recommend_your_favorite_movie
from RecommendMovie import recommend_other_favorite_movie
from pre_Process_Data import *


app = Flask(__name__)
#bootstrap = Bootstrap(app)
app.secret_key = '111'
#数据库

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@127.0.0.1/movie_re'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db =SQLAlchemy(app)
app.jinja_env.auto_reload = True
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app,supports_credentials=True)
CORS(app, resources=r'/*')

class Users(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(10))
    password = db.Column(db.String(255))
    email = db.Column(db.String(255))
    power = db.Column(db.String(255))
    gender = db.Column(db.String(255))
    age = db.Column(db.Integer)
    Job = db.Column(db.String(255))
    Zip_code = db.Column(db.String(255))

class Movies(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer,primary_key=True)
    name = db.Column(db.String(255))
    url = db.Column(db.String(255))
    time = db.Column(db.String(255))
    genre = db.Column(db.String(255))
    release_time = db.Column(db.String(255))
    intro = db.Column(db.String(255))
    directors = db.Column(db.String(255))
    writers = db.Column(db.String(255))
    starts = db.Column(db.String(255))
    year = db.Column(db.String(255))

# class Ratings(db.Model):
#     __tablename__ = 'ratings'
#     UserID = db.Column(db.Integer,ForeignKey("Users.id"))
#     MovieID = db.Column(db.Integer,ForeignKey("Movies.id"))
#     ratings = db.Column(db.Integer)

@app.route('/')
def index():
    #先判断是否登录
    user_id=session.get('user_id')
    user_power=session.get("power")
    username=session.get("username")
    if username:
        return render_template('index2.html',username=username)
    else:
        return render_template('page/template/login/login.html')


@app.route('/user')
def user():
    user_power = session.get("power")
    print(user_power)
    return render_template('page/system/user.html',power=user_power)

@app.route('/movies')
def moives():
    user_power = session.get("power")
    print(user_power)
    return render_template('page/system/movies.html',power=user_power)

@app.route('/type')
def type():
    return render_template('page/film/type.html')

@app.route('/bianhua')
def bianhua():
    return render_template('page/film/bianhua1.html')
@app.route('/center')
def center():
    return render_template('page/template/user-info.html')

@app.route('/login_render')
def login_render():
    return render_template('page/template/login/login.html')

@app.route('/register_render')
def register_render():
    return render_template('page/template/login/reg.html')

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        get_json = request.get_json()
        username = get_json['username']
        password = get_json['password']

        # print(username,password)

        if not all([username, password]):
            table_result = {"code": 500, "msg": "失败,请输入完整用户名和密码"}
        else:
            user = Users.query.filter(Users.username == username, Users.password == password).first()
            # print(user)
            if user :
                # print(user.power)
                session.clear()
                session['user_id'] = user.id
                session['power'] = user.power
                session['username'] = user.username
                session.permanent = True
                # print(session["power"])
                table_result = {"code": 200, "msg": "成功"}

            else:
                table_result = {"code": 500, "msg": "失败,用户不存在"}
                # print(table_result)

        return jsonify(table_result)

@app.route('/register', methods=["GET", "POST"])
def register():
    if request.method == 'POST':
        session.clear()
        get_json = request.get_json()
        username = get_json['username']
        password = get_json['password']
        # username = request.form.get('username')
        # password = request.form.get('password')
        # print(username,password)

        if not all([username, password]):
            table_result = {"code": 500, "msg": "请输入用户名和密码"}

        user = Users.query.filter(Users.username == username, Users.password == password).first()
        if user :

            table_result = {"code": 500, "msg": "用户已存在"}


        else:
            userid = db.session.query(func.max(Users.id)).scalar()
            userid += 1
            # session['user_id'] = userid
            # session.permanent = True
            p = Users(id=userid, username=username, password=password, power='user')
            db.session.add(p)
            db.session.commit()
            table_result = {"code": 200, "msg": "注册成功"}

        return jsonify(table_result)


@app.route('/logout',methods=["GET", "POST"])
def logout():
    session.clear()
    table_result = {"code": 200, "msg": "注销成功"}
    return jsonify(table_result)
    # return redirect(url_for('login'))
ALLOWED_EXTENSIONS=["txt","csv","xlsx"]
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'code': -1, 'filename': '', 'msg': 'No file part'})
        file = request.files['file']
        print(file)
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            return jsonify({'code': -1, 'filename': '', 'msg': 'No selected file'})
        else:
            print(file.filename)
            try:
                if file and allowed_file(file.filename):
                    origin_file_name = file.filename
                    filename = origin_file_name
                    # filename = secure_filename(file.filename)
                    basepath = os.path.dirname(__file__)  # 当前文件所在路径
                    print(basepath)

                    UPLOAD_PATH = os.path.join(basepath, 'upload_file_dir')

                    if os.path.exists(UPLOAD_PATH):
                        pass
                    else:
                        os.makedirs(UPLOAD_PATH)
                    file.save(os.path.join(UPLOAD_PATH, filename))

                    return jsonify({'code': 0, 'filename':origin_file_name, 'msg': '上传成功'})
                else:
                    return jsonify({'code': -1, 'filename': '', 'msg': 'File not allowed'})
            except Exception as e:
                print(e)
                print("yyy")
                return jsonify({'code': -1, 'filename': '', 'msg': 'Error occurred'})
    else:
        return jsonify({'code': -1, 'filename': '', 'msg': 'Method not allowed'})


@app.route('/uploadm', methods=['POST'])
def upload_filem():

    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return jsonify({'code': -1, 'filename': '', 'msg': 'No file part'})
        file = request.files['file']
        print(file)
        # if user does not select file, browser also submit a empty part without filename
        if file.filename == '':
            return jsonify({'code': -1, 'filename': '', 'msg': 'No selected file'})
        else:
            print(file.filename)
            try:
                if file and allowed_file(file.filename):
                    origin_file_name = file.filename
                    filename = origin_file_name
                    # filename = secure_filename(file.filename)
                    basepath = os.path.dirname(__file__)  # 当前文件所在路径
                    print(basepath)

                    UPLOAD_PATH = os.path.join(basepath, 'upload_file_dir')
                    print("1 ",UPLOAD_PATH)
                    if os.path.exists(UPLOAD_PATH):
                        pass
                    else:
                        os.makedirs(UPLOAD_PATH)

                    file.save(os.path.join(UPLOAD_PATH, filename))
                    # df1 = pd.read_excel(os.path.join(UPLOAD_PATH, filename))

                    # f = file.read()  # 文件内容
                    # data = xlrd.open_workbook(file_contents=f)
                    # table = data.sheets()[0]
                    # names = data.sheet_names()  # 返回book中所有工作表的名字
                    # status = data.sheet_loaded(names[0])  # 检查sheet1是否导入完毕
                    # nrows = table.nrows  # 获取该sheet中的有效行数
                    # ncols = table.ncols  # 获取该sheet中的有效列数
                    # for i in range(nrows-1):
                    #     s = table.row_values(i+1)
                    #     name = s[0]
                    #     url ,time,genre,  release_time, intro ,directors, writers, starts  = s[1],s[2], s[3], s[4], s[5], s[6], s[7], s[8]
                    #     if Movies.query.filter_by(name=name):
                    #         Movies.query.filter_by(id=int(id)).update({'name':name,"url":url, 'time':time, 'genre':genre,"writers":writers,
                    #                                                    "starts":starts,"release_time":release_time,"intro":intro,
                    #                                                    "directors":directors})
                    #         db.session.commit()
                    #     else:
                    #         movie = Movies()
                    #         movie.id = db.session.query(func.max(Movies.id)).scalar()
                    #         movie.id += 1
                    #         movie.name = name
                    #         movie.url = url
                    #         movie.time = time
                    #         movie.genre = genre
                    #         movie.release_time = release_time
                    #         movie.intro = intro
                    #         movie.directors = directors
                    #         movie.writers = writers
                    #         movie.starts = starts
                    #         db.session.add(movie)
                    #         db.session.commit()
                    return jsonify({'code': 0, 'filename':origin_file_name, 'msg': '上传成功'})
                else:
                    return jsonify({'code': -1, 'filename': '', 'msg': 'File not allowed'})
            except Exception as e:
                print(e)
                print("yyy")
                return jsonify({'code': -1, 'filename': '', 'msg': 'Error occurred'})
    else:
        return jsonify({'code': -1, 'filename': '', 'msg': 'Method not allowed'})

@app.route("/user/get",methods=['GET'])
def get_user():
    per_page = int(request.args['limit'])
    page = int(request.args['page'])
    username = request.args.get('username')
    print(username)

    user_id=session.get('user_id')
    user_power=session.get("power")
    data = []
    if user_power=="user":
        user = Users.query.filter(Users.id == user_id).first()

        if user:
            code=0
            count=1
            if user.gender == "F":
                gender = "女"
            else:
                gender = "男"
            item = {'id': user.id, 'username': user.username, 'gender': gender, 'email': user.email,
                    'age': user.age, 'Job': user.Job, 'Zip_code': user.Zip_code, "power": user.power, "password":user.password}
            data.append(item)

    elif username:

        count=Users.query.filter(Users.username.like('%' + username + '%')).count()
        users = Users.query.filter(Users.username.like('%' + username + '%')).limit(per_page).offset((page - 1) * per_page)

        if users:
            code = 0
            # count=len(users)
            for user in users:
                if user.gender == "F":
                    gender = "女"
                else:
                    gender = "男"
                item = {'id': user.id, 'username': user.username, 'gender': gender, 'email': user.email,
                        'age': user.age, 'Job': user.Job, 'Zip_code': user.Zip_code, "power": user.power, "password":user.password}
                data.append(item)
    else:
        count=Users.query.count()
        users = Users.query.limit(per_page).offset((page - 1) * per_page)
        if users:
            code = 0
            # count=len(users)
            for user in users:
                if user.gender == "F":
                    gender = "女"
                else:
                    gender = "男"
                item = {'id': user.id, 'username': user.username, 'gender': gender, 'email': user.email,
                        'age': user.age, 'Job': user.Job, 'Zip_code': user.Zip_code, "power": user.power, "password":user.password}
                data.append(item)



    res={
        "code":code,
        "msg":"",
        "count":count,
        "data":data

        }
    return jsonify(res)

@app.route("/user/del",methods=["GET","POST"])
def del_user():
    get_json = request.get_json()
    user_id = get_json.get("id","None")
    user_ids = get_json.get("ids")
    # print(user_id)
    # print(user_ids)
    if user_id:
       user = Users.query.filter(Users.id == user_id).first()
       db.session.delete(user)
       db.session.commit()
       table_result = {"code": 200, "msg": "成功"}
    elif user_ids:
        user_ids=user_ids.split(",")
        for id in user_ids:
            user = Users.query.filter(Users.id == id).first()
            db.session.delete(user)
            db.session.commit()
            table_result = {"code": 200, "msg": "成功"}

    else:
        table_result = {"code": 500, "msg": "失败"}
    return jsonify(table_result)


@app.route("/user/add",methods=["GET","POST"])
def add_user():

    username = request.args.get("username")
    Job = request.args.get("Job")
    Zip_code = request.args.get("Zip_code")
    age = request.args.get("age")
    email = request.args.get("email")
    gender = request.args.get("gender")
    power = request.args.get("power")
    password = request.args.get("password")
    if username =='':
        table_result = {"code": 500, "msg": "请输入用户名"}
    else:
        exist = Users.query.filter(Users.username == username).first()
        if exist:
            table_result = {"code": 500, "msg": "用户名已经存在"}
        else:
            user = Users()
            user.id = db.session.query(func.max(Users.id)).scalar()
            user.id += 1
            user.username=username
            user.Zip_code=Zip_code
            user.Job=Job
            user.age=age
            user.email=email
            user.gender=gender
            user.power=power
            user.password=password
            db.session.add(user)
            db.session.commit()
            table_result = {"code": 200, "msg": "新增用户成功"}
    return jsonify(table_result)


@app.route("/user/update",methods=["GET","POST"])
def update_user():
    id=request.args.get("id")
    username = request.args.get("username")
    Job = request.args.get("Job")
    Zip_code = request.args.get("Zip_code")
    age = request.args.get("age")
    email = request.args.get("email")
    gender = request.args.get("gender")
    power = request.args.get("power")
    password = request.args.get("password")

    if Users.query.filter_by(id=int(id)).update({'username':username, 'gender':gender, 'age':age,
                                                 "email":email, "Job":Job,"Zip_code":Zip_code,"password":password}):
        db.session.commit()
        table_result = {"code": 200, "msg": "修改成功"}
    else:
        table_result = {"code": 500, "msg": "修改失败"}

    return jsonify(table_result)


@app.route("/movie/get",methods=['GET'])
def get_movie():

    #分页查询
    print("test")
    per_page = int(request.args['limit'])
    page = int(request.args['page'])
    name=request.args.get("name")
    if name:
        count=Movies.query.filter(Movies.name.contains(name)).count()
        movies=Movies.query.filter(Movies.name.contains(name)).limit(per_page).offset((page - 1) * per_page)

    else:
        count=Movies.query.count()
        movies = Movies.query.limit(per_page).offset((page - 1) * per_page)
    data = []
    code=1
    print(movies)
    if movies:
        code=0
        for movie in movies:
            item = {'id': movie.id, 'name': movie.name, 'genre': movie.genre, 'intro': movie.intro,
                    'time': movie.time, 'url': movie.url, 'release_time': movie.release_time,
                    'directors': movie.directors,
                    'writers': movie.writers, 'starts': movie.starts}
            data.append(item)

    res={
        "code":code,
        "msg":"",
        "count":count,
        "data":data
        }
    return jsonify(res)

@app.route("/movie/del",methods=["GET","POST"])
def del_movie():
    get_json = request.get_json()
    id = get_json.get("id")
    ids = get_json.get("ids")

    if id:
       movie = Movies.query.filter(Movies.id == id).first()
       db.session.delete(movie)
       db.session.commit()
       table_result = {"code": 200, "msg": "成功"}
    elif ids:
        ids=ids.split(",")
        for id in ids:
            movie = Movies.query.filter(Movies.id == id).first()
            db.session.delete(movie)
            db.session.commit()
            table_result = {"code": 200, "msg": "成功"}

    else:
        table_result = {"code": 500, "msg": "失败"}
    return jsonify(table_result)


@app.route("/movie/add",methods=["GET","POST"])
def add_movie():
    name = request.args.get("name")
    url = request.args.get("url")
    time = request.args.get("time")
    genre = request.args.get("genre")
    release_time = request.args.get("release_time")
    intro = request.args.get("intro")
    directors = request.args.get("directors")
    writers = request.args.get("writers")
    starts = request.args.get("starts")

    movie = Movies()
    movie.id = db.session.query(func.max(Movies.id)).scalar()
    movie.id += 1
    movie.name=name
    movie.url=url
    movie.time=time
    movie.genre=genre
    movie.release_time=release_time
    movie.intro=intro
    movie.directors=directors
    movie.writers=writers
    movie.starts=starts
    db.session.add(movie)
    db.session.commit()
    table_result = {"code": 200, "msg": "新增用户成功"}
    return jsonify(table_result)


@app.route("/movie/update",methods=["GET","POST"])
def update_movie():
    id = request.args.get("id")
    name = request.args.get("name")
    print(name)
    url = request.args.get("url")
    time = request.args.get("time")
    genre = request.args.get("genre")
    release_time = request.args.get("release_time")
    intro = request.args.get("intro")
    directors = request.args.get("directors")
    writers = request.args.get("writers")
    starts = request.args.get("starts")

    if Movies.query.filter_by(id=int(id)).update({'name':name,"url":url, 'time':time, 'genre':genre,"writers":writers,"starts":starts,"release_time":release_time,"intro":intro,"directors":directors}):
        db.session.commit()
        table_result = {"code": 200, "msg": "修改成功"}
    else:
        table_result = {"code": 500, "msg": "修改失败"}

    return jsonify(table_result)
@app.route("/movies/get_year",methods=['GET'])
def movies_get_yaer():

    sql="SELECT `year` FROM movie GROUP BY year"
    conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='movie_re',
                           charset='utf8mb4')
    cursor = conn.cursor()
    cursor.execute(sql)
    values = cursor.fetchall()
    datas = []
    for index, i in enumerate(values):
        if i[0]:
            mydict = {}
            mydict["id"]=index
            mydict["name"]=i[0]
            datas.append(mydict)
    j = jsonify(datas)
    cursor.close()
    conn.close()
    print(j)
    return j


@app.route("/data/type_analyse_by_year",methods=["GET","POST"])
def movie_type_analyse_by_year():
    res={}
    yd = ['Action', 'Adventure', 'Animation', "Children's", 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy',
          'Film-Noir', 'Horror', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    yd_map = {"Action":"动作", "Adventure":"奇遇", "Animation":"动漫", "Children's":"儿童", "Comedy":"喜剧", "Crime":"犯罪", "Documentary":"纪录片",
              "Drama":"戏剧", "Fantasy":"幻想", "Film-Noir":"黑色", "Horror":"恐怖", "Musical":"音乐剧", "Mystery":"神秘", "Romance":"浪漫",
              "Sci-Fi":"科幻", "Thriller":"惊悚", "War":"战争", "Western":"西方"}
    xd=[]
    datas=[]
    data_year=None
    if (len(request.args) != 0):
        data_year = request.args['year']
    for item in yd:
        mydict = {}
        if data_year:
            print(data_year)
            num = Movies.query.filter(and_(Movies.genre.contains(item),Movies.year==data_year)).count()
        else:
            num=Movies.query.filter(Movies.genre.contains(item)).count()
        mydict["value"] = num
        mydict["name"] = yd_map[item]
        datas.append(mydict)
        xd.append(num)
        res['categories'] = yd
        res['data'] = xd
        res['datas'] = datas


    return jsonify(res)

@app.route("/data/count_analyse_by_type",methods=["GET","POST"])
def movie_count_analyse_by_type():
    if (len(request.args) != 0):
        data_type = request.args['type']
        if isinstance(data_type, str):
            sql = 'SELECT year,count(id) from movie where genre="%s"  GROUP BY `year`' % (data_type)
        else:
            sql = "SELECT year,count(id) from movie where genre=" + data_type + " GROUP BY `year`"
        # print(sql)
    else:
        sql = "SELECT year,count(id) from movie GROUP BY `year`"
    conn = pymysql.connect(host='localhost', user='root', password='root', port=3306, db='movie_re',
                           charset='utf8mb4')

    cursor = conn.cursor()
    cursor.execute(sql)
    values = cursor.fetchall()
    # print(values) #数组 ((2020, 155), (2021, 236), (2022, 4))

    mydict = {}
    for index, i in enumerate(values):

        mydict[i[0]] = i[1]
    print(mydict)
    j = jsonify(mydict)
    cursor.close()
    conn.close()
    return j


@app.route('/moviesremovie', methods=["GET", "POST"])
def moviesremovie():
    # get_json = request.get_json()
    # MovieID = get_json.get("id")
    MovieID = session.get('movie_id')
    UserID = session.get('user_id')
    print("movie",MovieID)
    print("user",UserID)

    User_Movie = getUserMovie(int(UserID))

    movie_chosen, movie_Rec1 = recommend_same_type_movie(int(MovieID), 20)

    hai = []
    for i in movie_Rec1:
        movie_id = i[0]
        movie_tem = Movies.query.filter(Movies.id == movie_id).first()
        # movie_hai = movie_tem.url
        # hai.append(movie_hai)
        # print('电影编码：',movie_tem)
        # print(type(movie_tem))
        if (movie_tem != None):
            movie_hai = movie_tem.url
            # print("海报：",movie_hai)
            # hai.append(movie_hai)

        else:
            movie_hai = '../static/images/images/portfolio/1.jpg'
            # hai.append(movie_hai)
        i = list(i)
        i.append(movie_hai)
        hai.append(i)
    hai = np.array(hai)
    # print("ihai=",hai)
    # print("recom=",movie_Rec1)

    print("开始执行完毕1")
    movie_Rec2 = recommend_your_favorite_movie(int(UserID), 10)
    print("开始执行完毕2")
    movie_Rec3 = recommend_other_favorite_movie(int(MovieID), 20)
    # print("re_3",movie_Rec3)
    hai_3 = []
    for i in movie_Rec3:
        movie_id_3 = i[0]
        movie_tem = Movies.query.filter(Movies.id == movie_id_3).first()

        if (movie_tem != None):
            movie_hai = movie_tem.url
            # print("海报：",movie_hai)
            # hai.append(movie_hai)

        else:
            movie_hai = '../static/images/images/portfolio/1.jpg'
            # hai.append(movie_hai)
        i = list(i)
        i.append(movie_hai)
        hai_3.append(i)
    hai_3 = np.array(hai_3)

    print("开始执行完毕3")
    # print("hai_3",hai_3)
    print('####')
    print(User_Movie)
    print('####')
    # print(movie_Rec1)
    print('####')

    return render_template('index.html', movie = movie_chosen,recommend1=hai,recommend2=movie_Rec2,recommend3=hai_3,userMovie=User_Movie,userID=int(UserID))


@app.route('/movie_search_res', methods=["GET", "POST"])
def repr_movie_search_res():
    table_result = {"code": 200, "msg": "成功"}

    get_json = request.get_json()
    MovieID = get_json.get("id")
    session['movie_id'] = MovieID
    session.permanent = True
    print("movie_id",MovieID)
    UserID = session.get('user_id')
    print("user_id",UserID)

    return jsonify(table_result)# ,redirect(url_for('removie', UserID=UserID, MovieID=MovieID))
    #return render_template('index.html', movie = movie_chosen,recommend1=hai,recommend2=movie_Rec2,recommend3=hai_3,userMovie=User_Movie,userID=int(UserID))

if __name__ == '__main__':
   app.run(debug = True,threaded=True)

