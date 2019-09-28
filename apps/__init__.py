from flask import Flask

from apps.views.article_view import article_bp
from apps.views.user_view import blog_bp
from exts import db, csrf, cache
from settings import DevelopmentConfig

config = {
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_HOST': '127.0.0.1',
    'CACHE_REDIS_PORT': 6379
}


def create_app():
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    app.config.from_object(DevelopmentConfig)
    # 给db对象初始化app
    db.init_app(app)
    csrf.init_app(app)
    cache.init_app(app, config=config)
    # 注册蓝图
    app.register_blueprint(blog_bp)
    app.register_blueprint(article_bp)

    return app
