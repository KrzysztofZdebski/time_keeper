from flask import Flask
from .config import Config
from .extensions import db
from .routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        from . import routes

    app.register_blueprint(main)

    return app