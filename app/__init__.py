from flask import Flask
from .config import Config
from .models import db
from .routes import main

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    

    with app.app_context():
        from . import routes
        from .models import User
        
        db.create_all()
        # user = User(email='email@gmail.com',password='password')
        # db.session.add(user)
        # db.session.commit()


    app.register_blueprint(main)


    return app