import datetime

from flask import Flask, render_template, request, make_response, url_for
from flask_login import LoginManager, login_user, login_required, current_user
from flask import abort
from werkzeug.utils import redirect

from data import db_session
from data.users import User
from forms.user import RegisterForm, LoginForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
db_session.global_init("db/blogs.db")
login_manager = LoginManager()
login_manager.init_app(app)
ac_pos = 0
max_cont_len = 1024 * 1024


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают", ak=ac_pos)
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть", ak=ac_pos)
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, ak=ac_pos)


@app.route('/login', methods=['GET', 'POST'])
def login():
    global ac_pos
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            ac_pos = 1
            return redirect("/main_page")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form, ak=ac_pos)
    return render_template('login.html', title='Авторизация', form=form, ak=ac_pos)


@app.route("/main_page")
def main_page():
    return render_template('main_page.html', title='Главная страница', ak=ac_pos)


@app.route("/menu")
def menu():
    return render_template('menu.html', title='Меню', ak=ac_pos)


@app.route("/cart")
def cart():
    return render_template('cart.html', title='Корзина', ak=ac_pos)


@app.route("/profile")
def prof():
    db_sess = db_session.create_session()
    us_id = current_user.get_id()
    user = db_sess.query(User).filter(User.id == us_id).first()
    return render_template('profile.html', title='Профиль', ak=ac_pos, user=user)


@app.route('/userava')
def userava():
    img = url_for('static', filename='img/shish.png')
    return img


if __name__ == '__main__':
   app.run(port=8080, host='127.0.0.1')

