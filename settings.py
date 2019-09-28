import os


class Config:
    DEBUG = False
    TESTING = False
    # mysql+pymysql://user:password@host:port/database
    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://gjp:976431@49.235.194.73:3306/test'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:root@127.0.0.1:3306/myblog'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    SECRET_KEY = 'hdfjds38948938bmbfsd90008'
    BASE_DIR = os.path.dirname(__file__)
    UPLOAD_DIR = os.path.join(BASE_DIR, 'static/upload')


class DevelopmentConfig(Config):
    DEBUG = True
    ENV = 'development'


class ProductionConfig(Config):
    DATABASE_URI = ''


class TestingConfig(Config):
    TESTING = True
