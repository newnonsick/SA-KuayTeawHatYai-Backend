from flask import Blueprint, jsonify

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello, World!!"})
