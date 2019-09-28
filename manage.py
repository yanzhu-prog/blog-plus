from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from apps.models.blog_model import User,Article
from apps import create_app
from exts import db

app = create_app()
manager = Manager(app)

# 给manager添加db命令
migrate = Migrate(app=app, db=db)
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()
