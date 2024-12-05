from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.exceptions import HTTPException

from app.utils import verify_token

from .config import Config
from .db import init_db

socketio = SocketIO(cors_allowed_origins="*")


def create_app():
    app = Flask(__name__)
    CORS(
        app,
        resources={"*": {"origins": "*"}},
    )

    app.config.from_object(Config)

    # Initialize SocketIO
    socketio.init_app(app)

    from . import socket_service

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

    from .routes.search import search_blueprint

    app.register_blueprint(search_blueprint)

    from .routes.income import income_blueprint

    app.register_blueprint(income_blueprint)

    @app.before_request
    def authenticate_request():
        """ตรวจสอบ Token ก่อนดำเนินการทุก Request"""
        exempt_routes = ["/"]

        if request.path in exempt_routes:
            return

        token = request.headers.get("Authorization")

        if not token:
            raise ValueError("Missing token authorization")

        if not verify_token(token):
            raise ValueError("Invalid or expired token")

    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        response = error.get_response()
        response.data = jsonify(
            {
                "code": error.code,
                "name": error.name,
                "description": error.description,
            }
        ).get_data(as_text=True)
        response.content_type = "application/json"
        return response

    @app.errorhandler(Exception)
    def handle_exception(error):
        print(f"An error occurred: {str(error)}")

        if isinstance(error, ValueError):
            return jsonify({"code": "Bad Request", "message": str(error)}), 400

        return (
            jsonify(
                {
                    "code": "Internal Server Error",
                    "message": "An error occurred. Please try again later.",
                }
            ),
            500,
        )

    return app
