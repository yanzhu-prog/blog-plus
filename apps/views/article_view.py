from flask import Blueprint, request, render_template, redirect, url_for, session

from apps.models.blog_model import Article, User, Comment
from exts import db

article_bp = Blueprint('article', __name__, url_prefix='/article')


@article_bp.before_app_request
def process_request():
    if request.path == '/article/add':
        username = session.get('uname')
        if not username:
            return render_template('login.html', msg='用户未登录，请登录！')


# 文章评论
@article_bp.route('/comment', endpoint='comment', methods=['POST'])
def article_comment():
    '''
       收： article_id content  user_id
            创建Comment对象  保存数据
            操作关系表(comment_user)： user_id   comment_id
       送:  跳转到详情页

    '''
    content = request.form.get('content')
    user_id = request.form.get('author')
    article_id = request.form.get('aid')
    # print(content,user_id,article_id)

    user = User.query.get(user_id)

    comment = Comment()
    comment.content = content
    comment.article_id = article_id

    user.comments.append(comment)  # user.comments.append(comment)
    db.session.commit()
    url = url_for('article.detail') + '?aid=' + str(article_id)
    return redirect(url)


# 文章详情
@article_bp.route('/detail', endpoint='detail')
def article_detail():
    aid = request.args.get('aid')
    # 找文章对象
    article = Article.query.get(aid)
    article.click_num += 1
    db.session.commit()
    users = User.query.all()
    return render_template('article_detail.html', article=article, users=users)


# 点赞
@article_bp.route('/love', endpoint='love')
def article_love():
    aid = request.args.get('aid')
    article = Article.query.get(aid)
    article.love_num += 1
    db.session.commit()

    return {'msg': 'ok', 'number': article.love_num}


# 发表文章
@article_bp.route('/add', endpoint='add', methods=['GET', 'POST'])
def article_add():
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        user_id = request.form.get('author')
        # 添加文章
        article = Article()
        article.title = title
        article.content = content
        #
        article.user_id = user_id

        db.session.add(article)
        db.session.commit()
        return redirect(url_for('blog.index'))
    else:
        users = User.query.all()
        return render_template('article_add.html', users=users)


@article_bp.route('/find_by_user', endpoint='find')
def find_by_user():
    uid = request.args.get('uid')
    user = User.query.get(uid)
    return render_template('user_article.html', user=user)
