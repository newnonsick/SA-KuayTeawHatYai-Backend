from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query

ingredients_blueprint = Blueprint('ingredients', __name__)

@ingredients_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello, World!"})


def validate_ingredient(data):
    """Validate the ingredient data."""
    if not data:
        raise ValueError("No data provided.")
    
    name = data.get("name")
    is_available = data.get("is_available")
    image_url = data.get("image_url")
    ingredient_type = data.get("ingredient_type")

    if not all([name, is_available, image_url, ingredient_type]):
        raise ValueError("Missing required fields.")
    
    if not isinstance(is_available, bool):
        raise ValueError("is_available must be a boolean.")
    
    return name, is_available, image_url, ingredient_type

def check_duplicate_ingredient(name):
    """Check for duplicate ingredients."""
    query = "SELECT * FROM INGREDIENT WHERE name = %s"
    result = fetch_query(query, (name,))

    return len(result) > 0



@ingredients_blueprint.route('/ingredients', methods=['GET'])
def get_ingredients():
    query = "SELECT * FROM INGREDIENT"
    result = fetch_query(query)
    
    ingredients = [{
        "name": item[0],
        "is_available": item[1],
        "image_url": item[2],
        "ingredient_type": item[3]
    } for item in result]
    
    return jsonify({"code": "success", "ingredients": ingredients})


@ingredients_blueprint.route('/ingredients/add', methods=['POST'])
def add_ingredients():
    data = request.get_json()
    name, is_available, image_url, ingredient_type = validate_ingredient(data)

    if check_duplicate_ingredient(name):
        raise ValueError("Ingredient already exists.")
    
    query = "INSERT INTO INGREDIENT (name, is_available, image_url, ingredient_type) VALUES (%s, %s, %s, %s)"
    result = execute_command(query, (name, is_available, image_url, ingredient_type))
    
    return jsonify({"code": "success", "message": "Ingredient added successfully."})


@ingredients_blueprint.route('/ingredients/delete', methods=['DELETE'])
def delete_ingredients():
    data = request.get_json()
    name = data.get("name")
    
    if not name:
        raise ValueError("Missing required fields.")
    
    query = "DELETE FROM INGREDIENT WHERE name = %s"
    result = execute_command(query, (name,))
    
    return jsonify({"code": "success", "message": "Ingredient deleted successfully."})


@ingredients_blueprint.route('/ingredients/update', methods=['PUT'])
def update_ingredients():
    data = request.get_json()
    name, is_available, image_url, ingredient_type = validate_ingredient(data)

    if not check_duplicate_ingredient(name):
        raise ValueError("Ingredient does not exist.")
    
    query = "UPDATE INGREDIENT WHERE name = %s SET is_available = %s, image_url = %s, ingredient_type = %s"
    result = execute_command(query, (name, is_available, image_url, ingredient_type))
    
    return jsonify({"code": "success", "message": "Ingredient updated successfully."})




















    

   
