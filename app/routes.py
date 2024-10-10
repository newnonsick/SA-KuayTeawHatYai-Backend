from flask import Blueprint, request, jsonify
from .db import execute_query

main_blueprint = Blueprint('main', __name__)


@main_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello, World!"})

@main_blueprint.route('/data', methods=['GET'])
def get_data():
    query = "SELECT * FROM some_table;"
    result = execute_query(query)
    return jsonify(result)

@main_blueprint.route('/data', methods=['POST'])
def insert_data():
    data = request.json
    query = "INSERT INTO some_table (column1, column2) VALUES (%s, %s);"
    params = (data['column1'], data['column2'])
    execute_query(query, params)
    return jsonify({"message": "Data inserted successfully"}), 201
