from http.client import HTTPException
from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query

menus_blueprint = Blueprint('menus', __name__)

def validate_menu_item(data):
    """Validate the menu item data."""
    if not data:
        raise ValueError("No data provided.")
    
    name = data.get("name")
    category = data.get("category")
    price = data.get("price")
    image_url = data.get("image_url")

    if not all([name, category, price, image_url]):
        raise ValueError("Missing required fields.")
    
    if not isinstance(price, (int, float)):
        raise ValueError("Price must be a number.")
    
    return name, category, price, image_url

def check_duplicate_menu(name):
    """Check for duplicate menu items."""
    query = "SELECT * FROM MENU WHERE name = %s"
    
    result = fetch_query(query, (name,))

    return len(result) > 0


@menus_blueprint.route('/menus/add', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    name, category, price, image_url = validate_menu_item(data)

    if check_duplicate_menu(name):
        raise ValueError("Menu item already exists.")
    
    query = "INSERT INTO MENU (name, category, price, image_url) VALUES (%s, %s, %s, %s)"
    result = execute_command(query, (name, category, price, image_url))
    
    return jsonify({"code": "success", "message": "Menu item added successfully."})


@menus_blueprint.route('/menus/delete', methods=['DELETE'])
def delete_menu_item():
    data = request.get_json()
    name = data.get("name")
    
    if not name:
        raise ValueError("Missing required fields.")
    
    query = "DELETE FROM MENU WHERE name = %s"
    result = execute_command(query, (name,))
    
    return jsonify({"code": "success", "message": "Menu item deleted successfully."})


@menus_blueprint.route('/menus', methods=['GET'])
def get_menu_items():
    category = request.args.get("category")
    query = "SELECT * FROM MENU" + (f" WHERE category = %s" if category else "")
    params = (category,) if category else ()

    result = fetch_query(query, params)
    
    menu_items = [{
        "name": item[0],
        "category": item[1],
        "price": item[2],
        "image_url": item[3]
    } for item in result]
    
    return jsonify({"code": "success", "menus": menu_items})


@menus_blueprint.route('/menus/update', methods=['PUT'])
def update_menu_item():
    data = request.get_json()
    name, category, price, image_url = validate_menu_item(data)

    if not check_duplicate_menu(name):
        raise ValueError("Menu item does not exist.")
    
    query = "UPDATE MENU SET category = %s, price = %s, image_url = %s WHERE name = %s"
    result = execute_command(query, (category, price, image_url, name))
    
    return jsonify({"code": "success", "message": "Menu item updated successfully."})

@menus_blueprint.route('/menus/ingredients', methods=['GET'])
def get_menu_item_ingredients():
    name = request.args.get("name")
    if not name:
        raise ValueError("Missing required fields.")
   
    query = "SELECT i.name, i.is_available, i.image_URL, i.ingredient_type FROM INGREDIENT i JOIN MENU_INGREDIENT mi ON i.name = mi.ingredient_name WHERE mi.menu_name = %s"
    result = fetch_query(query, (name,))

    ingredients = [{
        "name": item[0],
        "is_available": item[1],
        "image_URL": item[2],
        "ingredient_type": item[3]
    } for item in result]

    return jsonify({"code": "success", "ingredients": ingredients})
    
    # 
    
