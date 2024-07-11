from flask import Flask, render_template, url_for, request, flash, session, redirect, abort,g
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import datetime
from FDataBase import FDataBase
from flask_login import LoginManager,login_user,login_required
from UserLogin import UserLogin

# конфигурация
DATABASE = '/tmp/flsite.db'
DEBUG = True
SECRET_KEY = 'fdgfh78@#5?>gfhf89dx,v06k'
USERNAME = 'admin'
PASSWORD = '123'
app = Flask(__name__)
app.config['SECRET_KEY'] = '55bd0e5eafba522af51c798b496bb6b09d2b1097'
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path,'flsite.db')))
app.permanent_session_lifetime = datetime.timedelta(days=10)
login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):

    print("load_user")

    return UserLogin().fromDB(user_id, dbase)


def connect_db():

    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row

    return conn


def create_db():

    """Вспомогательная функция для создания таблиц БД"""
    db_1 = connect_db()

    with app.open_resource('sq_db.sql', mode = 'r') as f:

        db_1.cursor().executescript(f.read())

    db_1.commit()
    db_1.close()


def get_db():
    '''Соединение с БД, если оно еще не установлено'''
    if not hasattr(g,'link_db'):

        g.link_db = connect_db()

    return g.link_db


dbase = None

@app.before_request
def before_request():

    """Установление соединения с БД перед выполнением запроса"""
    global dbase
    db = get_db()
    dbase = FDataBase(db)



@app.teardown_appcontext
def close_db(error):
    '''Закрываем соединение с БД, если оно было установлено'''
    if hasattr(g,'link_db'):

        g.link_db.close()



@app.route("/index")
def index():
    return render_template('index.html',title="Главная страница")
@app.route("/category")
@login_required
def category():
    return render_template('category.html')
@app.route("/about")
def about():
    return render_template('about.html',title="О сайте")
@app.route("/work")
@login_required
def work():
    return render_template('work.html')
@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html', title="Страница не найдена")
@app.route("/register", methods=["POST", "GET"])
def register():

    if request.method == "POST":

        session.pop('_flashes', None)

        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
                and len(request.form['psw']) > 4 and request.form['psw'] == request.form['psw2']:

            hash = generate_password_hash(request.form['psw'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)

            if res:

                flash("Вы успешно зарегистрированы", "success")

                return redirect(url_for('login'))

            else:

                flash("Ошибка при добавлении в БД", "error")
                print("no")

        else:

            print("yes")
            flash("Неверно заполнены поля", "error")

    return render_template("register.html", menu=dbase.getMenu(), title="Регистрация")


@app.route("/login", methods=["POST", "GET"])
def login():

    if request.method == "POST":

        user = dbase.getUserByEmail(request.form['email'])

        if user and check_password_hash(user['psw'], request.form['psw']):

            userlogin = UserLogin().create(user)
            login_user(userlogin)
            flash("Вы вошли в свой аккаунт!","success")

            return redirect(url_for('index'))

        flash("Неверная пара логин/пароль", "error")

    return render_template("login.html", menu=dbase.getMenu(), title="Авторизация")

@app.route("/addPost", methods=["POST", "GET"])
def addPost():

    if request.method == "POST":

        if len(request.form['name']) > 4 and len(request.form['post']) > 10:

            res = dbase.addPost(request.form['name'], request.form['post'],request.form['url'])

            if not res:
                flash('Ошибка добавления статьи', category='error')

            else:

                flash('Статья добавлена успешно', category='success')

        else:

            flash('Ошибка добавления статьи', category='error')

    return render_template('post.html', menu=dbase.getMenu(), title="Добавление статьи")


if __name__ == "__main__":

    app.run(debug=True)
