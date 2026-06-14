import os
import datetime
from flask import Flask
from flask_socketio import SocketIO
from .models import db

# socket obj banano hocche
socketio = SocketIO()


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'shayak_arrow_2008'

    # session 30 din porjonto thakbe, browser bondho korle o login thakbe
    app.config['PERMANENT_SESSION_LIFETIME'] = datetime.timedelta(days=30)
    # environment variable e DATABASE_URL thakle (Render/Supabase) tai use hobe
    # na thakle local SQLite use hobe
    db_url = os.environ.get('DATABASE_URL')

    if db_url is not None:
        app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    else:
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)

    # socket ke connect kora hocche
    socketio.init_app(app)

    # blue print resister kora
    from .routes.auth import auth_bp
    from .routes.chat import chat_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(chat_bp)

    # event file ke import korte hobe na hole socket event kaj korbe na
    from .sockets import events

    with app.app_context():
        db.create_all()

    return app
