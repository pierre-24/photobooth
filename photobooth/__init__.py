import os
import shutil
import click

from flask import Flask
from flask.cli import with_appcontext
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

from photobooth import settings

db = SQLAlchemy(session_options={'expire_on_commit': False})
bootstrap = Bootstrap5()
limiter = Limiter(key_func=get_remote_address)


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

    # add CLI
    app.cli.add_command(init_command)

    # add blueprint
    from photobooth.views import bp
    app.register_blueprint(bp)

    return app
