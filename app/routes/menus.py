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

def isMenuExist(name):
    """Check for duplicate menu items."""
    query = "SELECT * FROM MENU WHERE name = %s"
    
    result = fetch_query(query, (name,))

    return len(result) > 0


@menus_blueprint.route('/menus/add', methods=['POST'])
def add_menu_item():
    data = request.get_json()
    name, category, price, image_url = validate_menu_item(data)

    if isMenuExist(name):
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

@menus_blueprint.route('/menus/<name>', methods=['GET'])
def get_menu_item(name):
    query = "SELECT * FROM MENU WHERE name = %s"
    result = fetch_query(query, (name,))

    if not result:
        raise ValueError("Menu item does not exist.")
    
    menu_item = {
        "name": result[0][0],
        "category": result[0][1],
        "price": result[0][2],
        "image_url": result[0][3]
    }
    
    return jsonify({"code": "success", "menu": menu_item})


@menus_blueprint.route('/menus/update', methods=['PUT'])
def update_menu_item():
    data = request.get_json()
    name, category, price, image_url = validate_menu_item(data)

    if not isMenuExist(name):
        raise ValueError("Menu item does not exist.")
    
    query = "UPDATE MENU SET category = %s, price = %s, image_url = %s WHERE name = %s"
    result = execute_command(query, (category, price, image_url, name))
    
    return jsonify({"code": "success", "message": "Menu item updated successfully."})

@menus_blueprint.route('/menus/ingredients', methods=['GET'])
def get_menu_item_ingredients():
    name = request.args.get("name")
    if not name:
        raise ValueError("Missing required fields. Please provide a menu item name.")
   
    query = """
        SELECT i.name, i.is_available, i.image_URL, i.ingredient_type 
        FROM INGREDIENT i 
        JOIN MENU_INGREDIENT mi ON i.name = mi.ingredient_name 
        WHERE mi.menu_name = %s
    """
    result = fetch_query(query, (name,))

    ingredients = {}
    for item in result:
        ingredient_type = item[3]
        if ingredient_type not in ingredients:
            ingredients[ingredient_type] = []

        ingredients[ingredient_type].append({
            "name": item[0],
            "is_available": item[1],
            "image_url": item[2]
        })

    formatted_ingredients = [
        {
            "type": ingredient_type,
            "options": ingredient_list
        }
        for ingredient_type, ingredient_list in ingredients.items()
    ]

    return jsonify({
        "code": "success",
        "ingredients": formatted_ingredients
    })

@menus_blueprint.route('/menu/ingredients-not-in-menu', methods=['GET'])
def get_ingredients_not_in_menu():
    name = request.args.get("name")
    if not name:
        raise ValueError("Missing required fields. Please provide a menu item name.")
    
    query = """
        SELECT i.name, i.is_available, i.image_URL, i.ingredient_type
        FROM INGREDIENT i
        WHERE i.name NOT IN (
            SELECT mi.ingredient_name
            FROM MENU_INGREDIENT mi
            WHERE mi.menu_name = %s
        )
    """
    result = fetch_query(query, (name,))

    ingredients = {}
    for item in result:
        ingredient_type = item[3]
        if ingredient_type not in ingredients:
            ingredients[ingredient_type] = []

        ingredients[ingredient_type].append({
            "name": item[0],
            "is_available": item[1],
            "image_url": item[2]
        })

    formatted_ingredients = [
        {
            "type": ingredient_type,
            "options": ingredient_list
        }
        for ingredient_type, ingredient_list in ingredients.items()
    ]

    return jsonify({
        "code": "success",
        "ingredients": formatted_ingredients
    })

@menus_blueprint.route('/menu/add-ingredient', methods=['POST'])
def add_ingredients_to_menu():
    data = request.get_json()
    menu_name = data.get("menu_name")
    ingredients = data.get("ingredients")

    if not all([menu_name, ingredients]):
        raise ValueError("Missing required fields.")
    
    if not isMenuExist(menu_name):
        raise ValueError(f"Menu item {menu_name} does not exist.")
    
    for ingredient in ingredients:
        
        # Check if ingredient exists
        query = "SELECT * FROM INGREDIENT WHERE name = %s"
        result = fetch_query(query, (ingredient,))
        if not result:
            raise ValueError(f"Ingredient {ingredient} does not exist.")
        
        # Check if ingredient is already added to the menu
        query = "SELECT * FROM MENU_INGREDIENT WHERE menu_name = %s AND ingredient_name = %s"
        result = fetch_query(query, (menu_name, ingredient))
        if result:
            raise ValueError(f"Ingredient {ingredient} is already added to the menu.")

        query = "INSERT INTO MENU_INGREDIENT (menu_name, ingredient_name) VALUES (%s, %s)"
        result = execute_command(query, (menu_name, ingredient))
    
    return jsonify({"code": "success", "message": "Ingredients added to menu successfully."})

    
