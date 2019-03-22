from flask_restful import abort

from flask import redirect, request
from flask import render_template as flask_render_template
import extra.auth as auth
from v1 import init as init_api_v1
from forms import *
from Bible_net_worth import Bible_of_k

from models import User, Bottle


def init_route(app, db):

    # Переопределение стандартного рендера, добавляет параметр auth_user
    def render_template(*args, **kwargs):
        kwargs['auth_user'] = auth.get_user()
        return flask_render_template(*args, **kwargs)

    init_api_v1(app, auth)  # Инициализация маршрутов для API

    @app.route('/')
    @app.route('/index')
    def index():
        if not auth.is_authorized():
            return render_template(
                'index.html',
                title='Главная',
            )
        bottle_list = Bottle.query.all()
        return render_template(
            'bottle-list.html',
            title="Главная",
            bottle_list=bottle_list
        )

    @app.route('/install')
    def install():
        db.create_all()
        return render_template(
            'install-success.html',
            title="Главная"
        )

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        has_error = False
        login = ''
        if request.method == 'POST':
            username = request.form['username']
            if auth.login(username, request.form['password']):
                return redirect('/')
            else:
                has_error = True
        return render_template(
            'login.html',
            title='Вход',
            login=login,
            has_error=has_error
        )

    @app.route('/logout', methods=['GET'])
    def logout():
        auth.logout()
        return redirect('/')

    @app.route('/user/create', methods=['GET', 'POST'])
    def registration():
        has_error = False
        form = UserCreateForm()
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            user = User.query.filter_by(username=username).first()
            if user:
                has_error = True
            else:
                User.add(username=username, password=password)
                auth.login(username, password)
                return redirect('/')
        return render_template(
            'registration.html',
            title='Зарегистрироваться',
            form=form,
            has_error=has_error
        )

    @app.route('/bottle', methods=['GET'])
    def bottle_list():
        if not auth.is_authorized():
            return redirect('/login')
        bottle_list = Bottle.query.filter_by(user_id=auth.get_user().id)
        return render_template(
            'bottle-list.html',
            title="Новости",
            bottle_list=bottle_list
        )

    @app.route('/bottle/create', methods=['GET', 'POST'])
    def bottle_create_form():
        if not auth.is_authorized():
            return redirect('/login')
        form = BottleCreateForm()
        if form.validate_on_submit():
            title = form.title.data
            select = request.form.get('comp_select')
            value = int(form.value.data)
            koeff = Bible_of_k[str(select)]
            Bottle.add(title=title, value=value, type=select, net_worth=koeff * value, user=auth.get_user())
            return redirect('/')
        return render_template(
            'bottle-create.html',
            title='Создать новость',
            Bible=[{'name': 'COLA'}, {'name': 'SPRITE'}, {'name': 'WATER'}],
            form=form

        )



    @app.route('/bottle/<int:id>')
    def bottle_view(id: int):
        if not auth.is_authorized():
            return redirect('/login')
        bottle = Bottle.query.filter_by(id=id).first()
        if not bottle:
            abort(404)
        if bottle.user_id != auth.get_user().id:
            abort(403)
        user = bottle.user
        return render_template(
            'bottle-view.html',
            title='Бутылка - ' + bottle.title,
            bottle=bottle,
            user=user
        )

    @app.route('/bottle/delete/<int:id>')
    def bottle_delete(id: int):
        if not auth.is_authorized():
            return redirect('/login')
        bottle = Bottle.query.filter_by(id=id).first()
        if bottle.user_id != auth.get_user().id:
            abort(403)
        Bottle.delete(bottle)
        return redirect('/bottle')

