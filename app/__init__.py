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
    from .routes.index import index_blueprint
    app.register_blueprint(index_blueprint)

    from .routes.menus import menus_blueprint
    app.register_blueprint(menus_blueprint)

    from .routes.ingredients import ingredients_blueprint
    app.register_blueprint(ingredients_blueprint)

    # Initialize SocketIO
    socketio.init_app(app)

    from . import socket_service

    return app
