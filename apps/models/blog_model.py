from datetime import datetime

from exts import db


class User(db.Model):
    __tablename__ = 'user1'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(12), nullable=False, unique=True)
    password = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(11))
    isdelete = db.Column(db.Boolean, default=False)
    rdatetime = db.Column(db.DateTime, default=datetime.now)
    icon = db.Column(db.String(200),nullable=True)
    # 代码
    articles = db.relationship('Article', backref='user')
    comments = db.relationship('Comment', backref='users', secondary='comment_user')

    def __str__(self):
        return self.username


class Article(db.Model):
    __tablename__ = 'article'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(255), nullable=False)
    pdatetime = db.Column(db.DateTime, default=datetime.now)
    love_num = db.Column(db.Integer, default=0)
    click_num = db.Column(db.Integer, default=0)
    # 建立两张表之间的关系
    user_id = db.Column(db.Integer, db.ForeignKey('user1.id'), nullable=False)
    comments = db.relationship('Comment', backref='article')

    def __str__(self):
        return self.title


# 评论 模型
class Comment(db.Model):
    __tablename__ = 'comment'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.String(255), nullable=False)
    cdatetime = db.Column(db.DateTime, default=datetime.now)
    article_id = db.Column(db.Integer, db.ForeignKey('article.id'), nullable=False)

    def __str__(self):
        return self.content


class Comment_user(db.Model):
    __tablename__ = 'comment_user'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user1.id'), nullable=False)
    comment_id = db.Column(db.Integer, db.ForeignKey('comment.id'), nullable=False)


'''
  user ---> comment
  article的评论  ----》 user
'''
