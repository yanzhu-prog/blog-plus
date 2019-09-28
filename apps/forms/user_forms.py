from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from wtforms import StringField, PasswordField, Form, DateTimeField, FileField, IntegerField
from wtforms.validators import Length, EqualTo


class RegisterForm(Form):
    username = StringField(label='用户名',
                           validators=[Length(max=12, min=6, message='用户名长度必须在6~12位之间')])  # ----> < input type='text' >
    password = PasswordField(label='密码', validators=[Length(max=12, min=6, message='密码长度必须在6~12位之间')])
    repassword = PasswordField(label='确认密码',
                               validators=[Length(max=12, min=6, message='密码长度必须在6~12位之间'),
                                           EqualTo('password', message='两次密码不一致')])
    phone = StringField(label='手机号码', validators=[Length(max=11, min=11, message='手机号码必须11位')])


class UserForm(FlaskForm):
    id = IntegerField(label='id')
    username = StringField(label='用户名',
                           validators=[Length(max=12, min=6, message='用户名长度必须在6~12位之间')])
    phone = StringField(label='手机号码', validators=[Length(max=11, min=11, message='手机号码必须11位')])

    rdatetime = DateTimeField(label='注册时间')

    icon = FileField(label='用户头像', validators=[FileAllowed(['jpg', 'png'], 'Images only!')])
