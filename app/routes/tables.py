from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query

tables_blueprint = Blueprint('tables', __name__)


def validate_table(data):
    """Validate the table data."""
    if not data:
        raise ValueError("No data provided.")
    
    table_number = data.get("table_number")

    if not table_number:
        raise ValueError("Missing required fields.")
    
    return table_number

def isTableExist(table_number):
    """Check for duplicate tables."""
    query = "SELECT * FROM TABLES WHERE table_number = %s"
    
    result = fetch_query(query, (table_number,))

    return len(result) > 0

@tables_blueprint.route('/tables/add', methods=['POST'])
def add_table():
    data = request.get_json()
    table_number = validate_table(data)

    if isTableExist(table_number):
        raise ValueError("Table already exists.")
    
    query = "INSERT INTO TABLES (table_number) VALUES (%s)"
    result = execute_command(query, (table_number,))
    
    return jsonify({"code": "success", "message": "Table added successfully."})

@tables_blueprint.route('/tables', methods=['GET'])
def get_tables():
    query = "SELECT * FROM TABLES"
    result = fetch_query(query)
    
    tables = [{
        "table_number": item[0]
    } for item in result]
    
    return jsonify({"code": "success", "tables": tables})

@tables_blueprint.route('/tables/delete', methods=['DELETE'])
def delete_table():
    data = request.get_json()
    table_number = data.get("table_number")
    
    if not table_number:
        raise ValueError("Missing required fields.")
    
    if not isTableExist(table_number):
        raise ValueError("Table does not exist.")
    
    query = "DELETE FROM TABLES WHERE table_number = %s"
    result = execute_command(query, (table_number,))
    
    return jsonify({"code": "success", "message": "Table deleted successfully."})

