from flask import Blueprint, jsonify, request
from http.client import HTTPException

error_blueprint = Blueprint("error", __name__)

@error_blueprint.errorhandler(HTTPException)
def handle_http_exception(error):
    response = error.get_response()
    response.data = jsonify({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    }).get_data(as_text=True)
    response.content_type = "application/json"
    return response


@error_blueprint.errorhandler(Exception)
def handle_exception(error):
    print(f"An error occurred: {str(error)}")
    
    if isinstance(error, ValueError):
        return jsonify({"error": "Bad Request", "message": str(error)}), 400
    
    return jsonify({"error": "Internal Server Error", "message": str(error)}), 500