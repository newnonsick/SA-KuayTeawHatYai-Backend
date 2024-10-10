from flask import Flask
from flask_socketio import SocketIO
from .config import Config
from .db import init_db

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize database
    init_db(app)

    # Register routes
    from .routes import main_blueprint
    app.register_blueprint(main_blueprint)

    # Initialize SocketIO
    socketio.init_app(app)

    return app
