from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query
import uuid
import datetime
from flask_socketio import emit

orders_blueprint = Blueprint('orders', __name__)

def validate_order(data):
    """Validate the order data."""
    if not data:
        raise ValueError("No data provided.")
    
    order_status = data.get("order_status")
    order_date = data.get("order_date")
    total_amount = data.get("total_amount")
    table_number = data.get("table_number")

    if not all([order_status, order_date, total_amount, table_number]):
        raise ValueError("Missing required fields.")
    
    if not isinstance(total_amount, (int, float)):
        raise ValueError("Total amount must be a number.")
    
    return order_status, order_date, total_amount, table_number

def isOrderExist(order_id):
    """Check for duplicate orders."""
    query = "SELECT * FROM ORDERS WHERE order_id = %s"
    
    result = fetch_query(query, (order_id,))

    return len(result) > 0

def validate_uuid(uuid_string):
    try:
        uuid.UUID(uuid_string)
    except ValueError:
        return False
    return True

@orders_blueprint.route('/orders', methods=['GET'])
def get_orders():
    status = request.args.get("status")
    table_number = request.args.get("table_number")

    if status and table_number:
        query = "SELECT * FROM ORDERS WHERE order_status = %s AND table_number = %s"
        result = fetch_query(query, (status, table_number))

    elif status:
        query = "SELECT * FROM ORDERS WHERE order_status = %s"
        result = fetch_query(query, (status,))
    
    elif table_number:
        query = "SELECT * FROM ORDERS WHERE table_number = %s"
        result = fetch_query(query, (table_number,))

    else:
        query = "SELECT * FROM ORDERS"
        result = fetch_query(query)

    orders = [{
        "order_id": item[0],
        "order_status": item[1],
        "order_date": item[2].strftime("%Y-%m-%d"),
        "total_amount": float(item[3]),
        "table_number": item[4]
    } for item in result]

    return jsonify({"code": "success", "orders": orders})

def isMenuExist(name):
    """Check for duplicate menus."""
    query = "SELECT * FROM MENU WHERE name = %s"
    result = fetch_query(query, (name,))

    return len(result) > 0

def isIngredientBelongToMenu(menu_name, ingredient_name):
    """Check if ingredient belongs to the menu."""
    query = "SELECT * FROM MENU_INGREDIENT WHERE menu_name = %s AND ingredient_name = %s"
    result = fetch_query(query, (menu_name, ingredient_name))

    return len(result) > 0

def isIngredientExist(name):
    """Check for duplicate ingredients."""
    query = "SELECT * FROM INGREDIENT WHERE name = %s"
    result = fetch_query(query, (name,))

    return len(result) > 0

def isTableExist(table_number):
    """Check for duplicate tables."""
    query = "SELECT * FROM TABLES WHERE table_number = %s"
    
    result = fetch_query(query, (table_number,))

    return len(result) > 0

def validate_order_item(orders):
    for order in orders:
        menu = order.get("menu")
        quantity = order.get("quantity")
        ingredients = order.get("ingredients")
        portion = order.get("portion")
        extra_info = order.get("extraInfo")

        if not all([menu, quantity, ingredients, portion]):
            raise ValueError("Missing required fields.")
        
        if not isMenuExist(menu.get("name")):
            raise ValueError("Menu does not exist.")
        
        if not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer.")
        
        if not isinstance(ingredients, list):
            raise ValueError("Ingredients must be a list.")
        
        for ingredient in ingredients:
            if not isIngredientExist(ingredient):
                raise ValueError("Ingredient does not exist.")
            
            if not isIngredientBelongToMenu(menu.get("name"), ingredient):
                raise ValueError("Ingredient does not belong to the menu.")
        
        if portion not in ["พิเศษ", "ธรรมดา"]:
            raise ValueError("Invalid portion.")
        
def getTotalPrice(orders):
    total_price = 0
    for order in orders:
        menu = order.get("menu")
        quantity = order.get("quantity")
        portion = order.get("portion")

        query = "SELECT price FROM MENU WHERE name = %s"
        result = fetch_query(query, (menu.get("name"),))
        price = result[0][0]

        if portion == "พิเศษ":
            price += 10
        
        total_price += price * quantity

    return total_price

@orders_blueprint.route('/orders/add', methods=['POST'])
def add_order():
    data = request.get_json()
    orders = data.get("orders")
    table_number = data.get("tableNumber")

    if not all([orders, table_number]):
        raise ValueError("Missing required fields.")
    
    if not isinstance(orders, list):
        raise ValueError("Orders must be a list.")
    
    if not isTableExist(table_number):
        raise ValueError("Table does not exist.")

    validate_order_item(orders)

    price = getTotalPrice(orders)

    order_id = str(uuid.uuid4())
    # check if order_id is unique
    while True:
        query = "SELECT * FROM ORDERS WHERE order_id = %s"
        result = fetch_query(query, (order_id,))

        if not result:
            break
        
        order_id = str(uuid.uuid4())

    order_date = datetime.datetime.now()

    query = "INSERT INTO ORDERS (order_id, order_status, order_datetime, total_amount, table_number) VALUES (%s, %s, %s, %s, %s)"

    execute_command(query, (order_id, "Pending", order_date, price, table_number))

    for order in orders:
        menu = order.get("menu")
        quantity = order.get("quantity")
        ingredients = order.get("ingredients")
        portion = order.get("portion")
        extra_info = order.get("extraInfo")

        query = "SELECT price FROM MENU WHERE name = %s"
        result = fetch_query(query, (menu.get("name"),))
        price = result[0][0]

        if portion == "พิเศษ":
            price += 10
        
        order_item_id = str(uuid.uuid4())

        # check if order_item_id is unique
        while True:
            query = "SELECT * FROM ORDER_ITEM WHERE order_item_id = %s"
            result = fetch_query(query, (order_item_id,))

            if not result:
                break
            
            order_item_id = str(uuid.uuid4())

        query = "INSERT INTO ORDER_ITEM (order_item_id, menu_name, order_id, quantity, price, portions, extra_info) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        execute_command(query, (order_item_id, menu.get("name"), order_id, quantity, price, portion, extra_info))

        for ingredient in ingredients:
            query = "INSERT INTO ORDER_INGREDIENT (order_item_id, ingredient_name) VALUES (%s, %s)"
            execute_command(query, (order_item_id, ingredient))

    emit('new_order', {"order_id": order_id}, broadcast=True)
    return jsonify({"code": "success", "message": "Order added successfully."})


@orders_blueprint.route('/orders/<id>', methods=['GET'])
def get_order(id):
    if not validate_uuid(id):
        raise ValueError("Invalid order ID.")

    query = "SELECT * FROM ORDERS WHERE order_id = %s"

    result = fetch_query(query, (id,))
    if not result:
        raise ValueError("Order does not exist.")
    
    order_info = {
        "order_id": result[0][0],
        "order_status": result[0][1],
        "order_date": result[0][2].strftime("%Y-%m-%d"),
        "total_amount": float(result[0][3]),
        "table_number": result[0][4]
    }

    query = "SELECT * FROM ORDER_ITEM WHERE order_id = %s"

    result = fetch_query(query, (id,))

    menus = []
    for item in result:
        query = "SELECT ingredient_name FROM ORDER_INGREDIENT WHERE order_item_id = %s"
        ingredients = fetch_query(query, (item[0],))
        
        order = {
            "menu": {
                "name": item[1]
            },
            "quantity": item[3],
            "ingredients": [ingredient[0] for ingredient in ingredients],
            "portion": item[5],
            "extraInfo": item[6]
        }
        menus.append(order)

    return jsonify({"code": "success", "order": order_info, "menus": menus})

@orders_blueprint.route('/orders/update-status', methods=['PUT'])
def update_status_order():
    data = request.get_json()
    order_id = data.get("order_id")
    order_status = data.get("order_status")

    if not all([order_id, order_status]):
        raise ValueError("Missing required fields.")
    
    if not validate_uuid(order_id):
        raise ValueError("Invalid order ID.")
    
    if not isOrderExist(order_id):
        raise ValueError("Order does not exist.")
    
    query = "UPDATE ORDERS SET order_status = %s WHERE order_id = %s"
    execute_command(query, (order_status, order_id))

    emit('update_order', {"order_id": order_id, "order_status": order_status}, broadcast=True)
    return jsonify({"code": "success", "message": "Order updated successfully."})



