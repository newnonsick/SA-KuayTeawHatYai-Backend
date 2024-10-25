from flask import Flask
from flask_socketio import SocketIO
from app.utils import verify_token
from .config import Config
from .db import init_db
from flask_cors import CORS

socketio = SocketIO()

def create_app():
    app = Flask(__name__)
    CORS(app)

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

    from .routes.tables import tables_blueprint
    app.register_blueprint(tables_blueprint)

    from .routes.orders import orders_blueprint
    app.register_blueprint(orders_blueprint)

    # รอทุกอย่างเรียบร้อยแล้ว ค่อยใช้
    # @app.before_request
    # def authenticate_request():
    #     """ตรวจสอบ Token ก่อนดำเนินการทุก Request"""
    #     exempt_routes = ['/']

    #     if request.path in exempt_routes:
    #         return

    #     token = request.headers.get("Authorization")

    #     if not token:
    #         raise ValueError("Missing token or client ID")

    #     if not verify_token(token):
    #         raise ValueError("Invalid or expired token")

    # Initialize SocketIO
    socketio.init_app(app)

    from . import socket_service

    return app
