from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, IntegerField, FloatField, DateField, TextAreaField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo
from app.models import User


class LoginForm(FlaskForm):
    username = StringField('Пользователь', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Пользователь', validators=[DataRequired()])
    email = StringField(
        'E-mail', validators=[DataRequired(), Email(message="Неверный адрес электронной почты")])
    phone = StringField('Телефон', validators=[DataRequired()])
    #inn = StringField('ИНН', validators=[DataRequired()])
    #kpp = StringField('КПП')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Подтверждение пароля',
                              validators=[DataRequired(), EqualTo('password', message="Поле должно быть равно паролю")])
    submit = SubmitField('Регистрация')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(
                'Пожалуйста, используйте другое имя пользователя')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                'Пожалуйста, используйте другой электронный адрес')


class FormOrder(FlaskForm):
    supplier = StringField(
        'Поставщик', default="ООО ТД Шкуренко", validators=[])
    buyer = StringField('Покупатель', validators=[DataRequired()])
    delivery_date = DateField('Дата поставки', validators=[DataRequired()])
    consignee = SelectField('Адрес доставки', validators=[], choices=[])
    comment = TextAreaField('Комментарий', validators=[])
    #submit = SubmitField('Оформить заказ')


class FormProfile(FlaskForm):
    name = StringField('Наименование')
    email = StringField('E-mail')
    phone = StringField('Телефон')
    inn = StringField('ИНН')
    kpp = StringField('КПП')
    consignee = SelectField('Адреса доставки', choices=[])
    contracts = SelectField('Контракты', choices=[])
    catalog_exp = StringField('Каталог для экспорта накладных')
    file_type_exp = SelectField('Тип файла для экспорта', choices=[])
