__version__ = "0.1.0"

from flask import Flask
from .config import Config
from .routes import rt, socket


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    socket.init_app(app)

    app.register_blueprint(rt)

    return app
