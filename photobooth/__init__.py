import os
import shutil
import click

from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import flask_login

from photobooth.filters import filters

from photobooth import settings

db = SQLAlchemy(session_options={'expire_on_commit': False})
bootstrap = Bootstrap5()
limiter = Limiter(key_func=get_remote_address)
login_manager = flask_login.LoginManager()


class User(flask_login.UserMixin):
    def __init__(self, id_):
        super().__init__()
        self.id = id_


@login_manager.user_loader
def load_user(login):
    if login != settings.APP_CONFIG['USERNAME']:
        return

    return User(login)


@click.command('init')
@with_appcontext
def init_command():
    """Initializes stuffs:
    + directories
    + database
    + bootstrap data
    """

    # directories
    data_dir = settings.DATA_DIRECTORY

    if os.path.exists(data_dir):
        shutil.rmtree(data_dir)

    os.mkdir(data_dir)
    print('!! Data directory in {}'.format(data_dir))

    # DB:
    from photobooth.models import Request
    db.create_all()
    print('!! database created')


def create_app():
    app = Flask(__name__)
    app.config.update(settings.APP_CONFIG)

    # init stuffs
    db.init_app(app)
    bootstrap.init_app(app)
    limiter.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = 'admin.login'  # automatic redirection

    # add CLI
    app.cli.add_command(init_command)

    # add blueprint
    from photobooth.views import bp_main, bp_admin
    app.register_blueprint(bp_main)
    app.register_blueprint(bp_admin)

    # add filters
    app.jinja_env.filters.update(**filters)

    return app
