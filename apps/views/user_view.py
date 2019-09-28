import hashlib
import json
import os
import time
from io import BytesIO

import requests
from flask import Blueprint, render_template, request, redirect, url_for, make_response, session, abort, flash
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import or_

from apps.forms.user_forms import RegisterForm, UserForm
from apps.models.blog_model import User, Article
from apps.utils.util import validate_picture
from exts import db, cache
from settings import Config

blog_bp = Blueprint('blog', __name__, url_prefix='/blog')

# 路由列表
required_login = ['/blog/userall', '/blog/test']


@blog_bp.before_app_first_request
def first_test():
    print('------------------》 first_test')


@blog_bp.before_app_request
def process_request():
    # print('+++++++++++++++> before_app_request')
    # print(request.path)
    if request.path in required_login:
        # 需要进行登录验证
        username = session.get('uname')
        if not username:
            return render_template('login.html', msg='用户未登录，请登录！')


@blog_bp.after_app_request
def process_response(response):
    print('*****************> after_app_request')
    # response = make_response('error')
    return response


@blog_bp.errorhandler(404)
def handler_404(error):
    print(error)
    return render_template('404.html')


@blog_bp.errorhandler(500)
def handler_500(error):
    print(error)  # error 表示的是error对象
    return render_template('500.html')


#   七牛云存储
@blog_bp.route('/qiniu', endpoint='qiniu', methods=['GET', 'POST'])
def use_qiniu():
    if request.method=='POST':
        fs_picture = request.files.get('picture')


    return render_template('pic_upload.html')


# 测试函数
@blog_bp.route('/test', endpoint='test')
def user_test():
    print('===============>user_test')
    # abort(404)
    # abort(500)
    return 'OK'


# 用户详情
@blog_bp.route('/udetial', endpoint='udetail')
def user_detail():
    uname = session.get('uname')
    user = User.query.filter(User.username == uname).first()
    if user:
        # 用户的详情页
        uform = UserForm(obj=user)

        return render_template('user_detail.html', uform=uform, user=user)


# 首页
@blog_bp.route('/', endpoint='index')
def index():
    # 获取页码数  设置默认值
    page = request.args.get('page', 1)
    # 分页器对象
    paginate = Article.query.paginate(page=int(page), per_page=3)
    print(paginate.page)
    return render_template('index.html', paginate=paginate)


# 用户更新
@blog_bp.route('/update', endpoint='update', methods=['GET', 'POST'])
def user_update():
    if request.method == 'GET':
        id = request.args.get('id')
        user = User.query.get(id)  # 要更新的用户对象
        return render_template('update.html', user=user)
    else:
        # id = request.form.get('id')
        # username = request.form.get('username')
        # phone = request.form.get('phone')
        # isdelete = request.form.get('isdelete')

        user_form = UserForm(request.form)
        if user_form.validate():
            id = user_form.data.get('id')
            user = User.query.get(id)
            username = user_form.data.get('username')
            phone = user_form.data.get('phone')
            print('====>1', user_form.icon.data)
            print('====>2', user_form.data.get('icon'))
            icon = request.files.get('icon')  # icon  其实是一个FileStorage对象：属性filename  方法：save(path)
            # 用户保存到本地upload文件夹
            print(icon.filename)
            image_url = os.path.join(Config.UPLOAD_DIR, icon.filename)
            icon.save(image_url)
            # 保存到数据库中
            user.username = username
            user.phone = phone
            user.icon = 'upload/' + icon.filename
            db.session.commit()
            # flash('修改成功！')
            return redirect(url_for('blog.index'))
        else:
            return user_form.errors


# 用户删除
@blog_bp.route('/delete/<id>', endpoint='delete')
def user_delete(id):
    user = User.query.get(id)  # 根据主键查找对象
    # print(user)
    db.session.delete(user)  # 物理删除
    # user.isdelete = True
    db.session.commit()
    return redirect(url_for('blog.uall'))


# 用户检索
@blog_bp.route('/search', endpoint='search', methods=['POST'])
def user_search():
    search = request.form.get('search')
    if search:
        # users = User.query.filter(or_(User.username==search,
        #                       User.phone == search)).all()  # select * from user where username=search or phone=search
        # number = User.query.filter(or_(User.username==search,
        #                       User.phone == search)).count()
        users = User.query.filter(or_(User.username.contains(search), User.phone == search)).all()
        number = User.query.filter(or_(User.username.contains(search), User.phone == search)).count()
        return render_template('user_all.html', users=users, number=number)
    else:
        return redirect(url_for('blog.index'))


# 显示所有用户
@blog_bp.route('/userall', endpoint='uall')
def user_all():
    # users = User.query.filter_by(isdelete=False).all()
    # users = User.query.filter(User.isdelete == False, User.phone.startswith('150')).order_by(-User.rdatetime)
    users = User.query.all()
    number = User.query.count()
    return render_template('user_all.html', users=users, number=number)


# 用户退出
@blog_bp.route('/exit', endpoint='exit')
def user_exit():
    # cookie 的退出方式
    # response = redirect(url_for('blog.index'))
    # response.delete_cookie('uname')
    # response.delete_cookie('test')
    # response.set_cookie()
    # return response

    # session 的退出方式
    session.clear()
    return redirect(url_for('blog.index'))


# 获取手机号码，并向网易云信发送请求
@blog_bp.route('/send', endpoint='send')
def send_request():
    # 获取phone
    phone = request.args.get('phone')
    url = 'https://api.netease.im/sms/sendcode.action'  # 网易云信接口
    headers = {}
    headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=utf-8'
    AppSecret = 'ee8d51d1061e'
    Nonce = '74093849032804'
    CurTime = str(time.time())
    headers['AppKey'] = 'cc735ffe22684cc4dab2dc943540777c'
    headers['Nonce'] = Nonce
    headers['CurTime'] = CurTime
    s = AppSecret + Nonce + CurTime
    headers['CheckSum'] = hashlib.sha1(s.encode('utf-8')).hexdigest().lower()
    res = requests.post(url, data={'mobile': phone}, headers=headers)
    print(res.text, type(res.text))
    json_obj = json.loads(res.text)  # 字典
    cache.set(phone, json_obj.obj)
    # print(res.content)
    if json_obj.code == 200:
        return {'msg': 'success'}
    else:
        return {'msg': 'fail'}


# # 手机验证码和缓存的登录
# @blog_bp.route('/login', endpoint='login', methods=['GET', 'POST'])
# def user_login():
#     if request.method == 'POST':
#         # 主要做登录
#         phone = request.form.get('phone')
#         validate = request.form.get('valiadate')
#         code = cache.get(phone)
#         if code == validate:
#             user = User.query.filter(User.phone == phone).first()
#             cache.set('uname', user.username)
#             session['uname'] = user.username
#             return redirect(url_for('blog.index'))
#         else:
#             flash('手机验证码错误')
#             return render_template('login_phonecode.html')
#     return render_template('login_phonecode.html')


@blog_bp.route('/pic', endpoint='pic')
def get_pic():
    # 造图片
    im, s = validate_picture(4)
    print('=====>s:', s)
    # 将图片转成二进制的形式
    buffer = BytesIO()
    im.save(buffer, 'jpeg')
    buf_bytes = buffer.getvalue()
    # 构建response对象
    response = make_response(buf_bytes)
    response.headers['Content-Type'] = 'image/jpg'
    # 保存s
    # session['pic_code'] = s
    cache.set('code_abc', s, timeout=120)
    print('---------->', s)
    return response


# 图片验证码和缓存的登录
@blog_bp.route('/login', endpoint='login', methods=['GET', 'POST'])
def user_login():
    if request.method == 'POST':
        username = request.form.get('username')
        pwd1 = request.form.get('password1')
        captcha = request.form.get('captcha')
        # 从session中取值
        # code = session.get('pic_code')
        code = cache.get('code_abc')
        if code.lower() != captcha.lower():
            flash('验证码错误')
            return render_template('login_captcha.html')
        # 查询
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, pwd1):
            session['uname'] = username
            return redirect(url_for('blog.index'))
    else:
        print('login')
        return render_template('login_captcha.html')


# # 用户登录
# @blog_bp.route('/login', endpoint='login', methods=['GET', 'POST'])
# def user_login():
#     if request.method == 'POST':
#         username = request.form.get('username')
#         pwd1 = request.form.get('password1')
#         pwd = hashlib.sha1(pwd1.encode('utf-8')).hexdigest()
#         # 查询
#         user = User.query.filter_by(username=username).first()  # select * from user where username=xxxx
#         if pwd == user.password:
#             # cookie 记录在客户端的一种方式
#             # 写cookie要通过response对象完成
#             # response = make_response('用户登录成功！')
#             # response.set_cookie('uname', username)
#             # response.set_cookie('test', '123')
#             # response = redirect(url_for('blog.index'))
#             # response.set_cookie('uname', username)
#             # return response
#
#             # session 机制  记录登录状态
#             session['uname'] = username
#
#             return redirect(url_for('blog.index'))
#
#         else:
#             return render_template('login.html', msg='用户名或者密码有误！')
#
#     return render_template('login.html')


@blog_bp.route('/register', endpoint='register', methods=['GET', 'POST'])
def user_register():
    if request.method == 'GET':
        rform = RegisterForm()  # 创建表单类对象
        return render_template('register1.html', rform=rform)
    else:
        rform = RegisterForm(request.form)

        if rform.validate():  # 表示所有的验证是通过的
            username = rform.data.get('username')
            password = rform.data.get('password')
            phone = rform.data.get('phone')

            # 加密
            password = generate_password_hash(password)

            # 保存到数据库中
            # 1. 创建模型对象
            user = User()
            # 2. 给对象赋值
            user.username = username
            user.password = password
            user.phone = phone
            # 3. 向数据库提交数据
            db.session.add(user)
            db.session.commit()
            return redirect(url_for('blog.index'))

        else:
            return render_template('register1.html', rform=rform)
# 用户注册
# @blog_bp.route('/register', endpoint='register', methods=['GET', 'POST'])
# def user_register():
#     if request.method == 'POST':
#         # 获取表单提交的内容
#         username = request.form.get('username')
#         pwd1 = request.form.get('password1')
#         pwd2 = request.form.get('password2')
#         phone = request.form.get('phone')
#         if pwd1 == pwd2:
#             # 存放到数据库
#             pwd = hashlib.sha1(pwd1.encode('utf-8')).hexdigest()
#             print(pwd)
#             # 添加数据步骤:
#             # 1. 创建模型对象
#             user = User()
#             # 2. 给对象赋值
#             user.username = username
#             user.password = pwd
#             user.phone = phone
#             # 3. 向数据库提交数据
#             db.session.add(user)
#             db.session.commit()
#             return redirect(url_for('blog.index'))
#
#         else:
#             return render_template('register.html', msg=' 密码不一致')
#
#     return render_template('register.html')
