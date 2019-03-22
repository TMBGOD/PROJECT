from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, BooleanField, SelectField, FloatField, FieldList, FormField
from wtforms.validators import DataRequired
import Bible_net_worth


class BottleCreateForm(FlaskForm):
    title = StringField('Название партии бутылок', validators=[DataRequired()])
    value = FloatField('Объём', validators=[DataRequired()])
    net_worth = FloatField('Цена')
    type = StringField('Тип бутылки')
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class UserCreateForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Создать')
