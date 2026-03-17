from flask import Flask
from flask_migrate import Migrate
from flask_login import LoginManager

app = Flask(__name__)
from .config import Config

app.config.from_object(Config)

from .db import db

db.init_app(app)
from .models import User

migrate = Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
with app.app_context():
    db.create_all()

login_manager.login_view = 'user.login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


from .routes import main_bp, user_bp, dash_bp

app.register_blueprint(main_bp)
app.register_blueprint(user_bp)
app.register_blueprint(dash_bp)
