from flask import Blueprint, jsonify, json
from http.client import HTTPException
from .db import execute_query

main_blueprint = Blueprint('main', __name__)

@main_blueprint.errorhandler(HTTPException)
def handle_http_exception(error):
    response = error.get_response()
    response.data = json.dumps({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    })
    response.content_type = "application/json"
    return response

@main_blueprint.errorhandler(Exception)
def handle_exception(error):
    print(error)
    response = jsonify({"error": "Internal Server Error"})
    response.status_code = 500
    return response

@main_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello, World!"})



