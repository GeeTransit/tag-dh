import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    print(app.instance_path)
    app.config.from_mapping(
        SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_key'),
        SQLALCHEMY_DATABASE_URI = os.environ.get(
            'DATABASE_URL',
            'sqlite:///' + os.path.join(app.instance_path, 'tag_dh.sqlite')
        ),
        SQLALCHEMY_TRACK_MODIFICATIONS = False
    )

    db.init_app(app)
    migrate.init_app(app, db)
    from . import models

    from . import task_list
    from . import clash
    app.register_blueprint(task_list.bp)
    app.register_blueprint(clash.bp)

    return app

if __name__ == '__main__':
    app.run()
