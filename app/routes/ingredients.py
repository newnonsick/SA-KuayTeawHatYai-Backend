from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query

ingredients_blueprint = Blueprint('ingredients', __name__)

def validate_ingredient(data):
    """Validate the ingredient data."""
    if not data:
        raise ValueError("No data provided.")
    
    name = data.get("name")
    is_available = data.get("is_available")
    image_url = data.get("image_url")
    ingredient_type = data.get("ingredient_type")

    if not all([name, is_available in [True, False], image_url, ingredient_type]):
        raise ValueError("Missing required fields.")
    
    if not isinstance(is_available, bool):
        raise ValueError("is_available must be a boolean.")
    
    return name, is_available, image_url, ingredient_type

def isIngredientExist(name):
    """Check for duplicate ingredients."""
    query = "SELECT * FROM INGREDIENT WHERE name = %s"
    result = fetch_query(query, (name,))

    return len(result) > 0



@ingredients_blueprint.route('/ingredients', methods=['GET'])
def get_ingredients():
    query = "SELECT * FROM INGREDIENT ORDER BY ingredient_type"
    result = fetch_query(query)
    
    ingredients = [{
        "name": item[0],
        "is_available": item[1],
        "image_url": item[2],
        "ingredient_type": item[3]
    } for item in result]
    
    return jsonify({"code": "success", "ingredients": ingredients})

@ingredients_blueprint.route('/ingredients/<name>', methods=['GET'])
def get_ingredient(name):
    query = "SELECT * FROM INGREDIENT WHERE name = %s"
    result = fetch_query(query, (name,))
    
    if not result:
        raise ValueError("Ingredient does not exist.")
    
    ingredient = {
        "name": result[0][0],
        "is_available": result[0][1],
        "image_url": result[0][2],
        "ingredient_type": result[0][3]
    }
    
    return jsonify({"code": "success", "ingredient": ingredient})


@ingredients_blueprint.route('/ingredients/add', methods=['POST'])
def add_ingredients():
    data = request.get_json()
    name, is_available, image_url, ingredient_type = validate_ingredient(data)

    if isIngredientExist(name):
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
    
    if not isIngredientExist(name):
        raise ValueError("Ingredient does not exist.")
    
    query = "DELETE FROM INGREDIENT WHERE name = %s"
    result = execute_command(query, (name,))
    
    return jsonify({"code": "success", "message": "Ingredient deleted successfully."})


@ingredients_blueprint.route('/ingredients/update', methods=['PUT'])
def update_ingredients():
    data = request.get_json()
    name, is_available, image_url, ingredient_type = validate_ingredient(data)

    if not isIngredientExist(name):
        raise ValueError("Ingredient does not exist.")
    
    query = "UPDATE INGREDIENT SET is_available = %s, image_url = %s, ingredient_type = %s WHERE name = %s "
    result = execute_command(query, (is_available, image_url, ingredient_type, name))
    
    return jsonify({"code": "success", "message": "Ingredient updated successfully."})


@ingredients_blueprint.route('/ingredients/update-status', methods=['PUT'])
def update_ingredient_status():
    data = request.get_json()
    name = data.get("name")
    is_available = data.get("is_available")
    
    if not name or is_available is None:
        raise ValueError("Missing required fields.")
    
    if not isIngredientExist(name):
        raise ValueError("Ingredient does not exist.")
    
    query = "SELECT is_available FROM INGREDIENT WHERE name = %s"
    result = fetch_query(query, (name,))

    if result[0][0] == is_available:
        raise ValueError(f"Ingredient status is already set to the provided value ({is_available}).")
    
    query = "UPDATE INGREDIENT SET is_available = %s WHERE name = %s"
    result = execute_command(query, (is_available, name))

    if not is_available:
        query = """
            UPDATE ORDER_ITEM SET orderitem_status = 'เปลี่ยนวัตถุดิบ'
            WHERE order_item_id IN (
                SELECT order_item_id FROM ORDER_INGREDIENT
                WHERE ingredient_name = %s
            ) AND orderitem_status != 'เสร็จสิ้น'
        """
        result = execute_command(query, (name,))

    
    return jsonify({"code": "success", "message": "Ingredient status updated successfully."})




















    

   
