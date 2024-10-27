from flask import Blueprint, jsonify, request
from ..socket_service import socketio
from ..db import execute_command, fetch_query
import uuid
import datetime

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
    order_date = request.args.get("date")

    query = "SELECT * FROM ORDERS"
    conditions = []
    params = []

    if status:
        conditions.append("order_status = %s")
        params.append(status)

    if table_number:
        conditions.append("table_number = %s")
        params.append(table_number)

    if order_date:
        try:
            date_obj = datetime.datetime.strptime(order_date, "%Y-%m-%d").date()
            conditions.append("DATE(order_datetime) = %s")
            params.append(date_obj)
        except ValueError:
            return jsonify({"code": "error", "message": "Invalid date format, use YYYY-MM-DD"}), 400

    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    result = fetch_query(query, tuple(params))

    orders = [{
        "order_id": item[0],
        "order_status": item[1],
        "order_datetime": item[2].strftime("%Y-%m-%d %H:%M:%S"),
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

def isIngredientAvailable(name):
    """Check if ingredient is available."""
    query = "SELECT is_available FROM INGREDIENT WHERE name = %s"
    result = fetch_query(query, (name,))

    return result[0][0]

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

        if not all([menu, quantity]):
            raise ValueError("Missing required fields.")
        
        if not isMenuExist(menu.get("name")):
            raise ValueError("Menu does not exist.")
        
        if not isinstance(quantity, int):
            raise ValueError("Quantity must be an integer.")
        
        # if not isinstance(ingredients, list):
        #     raise ValueError("Ingredients must be a list.")
        
        if ingredients:
            for ingredient in ingredients:
                if not isIngredientExist(ingredient):
                    raise ValueError(f"Ingredient {ingredient} does not exist.")
                
                if not isIngredientAvailable(ingredient):
                    raise ValueError(f"Ingredient {ingredient} is not available.")
                
                if not isIngredientBelongToMenu(menu.get("name"), ingredient):
                    raise ValueError(f"Ingredient {ingredient} does not belong to the menu {menu.get("name")}.")
        if portion:
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

        query = "INSERT INTO ORDER_ITEM (order_item_id, menu_name, order_id, quantity, price, portions, extra_info, orderitem_status) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
        execute_command(query, (order_item_id, menu.get("name"), order_id, quantity, price, portion, extra_info, "Pending"))

        if ingredients:
            for ingredient in ingredients:
                query = "INSERT INTO ORDER_INGREDIENT (order_item_id, ingredient_name) VALUES (%s, %s)"
                execute_command(query, (order_item_id, ingredient))

    socketio.emit('new_order', {"order_id": order_id})
    return jsonify({"code": "success", "message": "Order added successfully."})


@orders_blueprint.route('/orders/<id>', methods=['GET'])
def get_order(id):
    if not validate_uuid(id):
        raise ValueError("Invalid order ID.")
    
    if not isOrderExist(id):
        raise ValueError("Order does not exist.")

    query = """
    SELECT 
        o.order_id,
        o.order_status,
        o.order_datetime,
        o.total_amount,
        o.table_number,
        oi.order_item_id,
        oi.menu_name,
        oi.quantity,
        oi.portions,
        oi.extra_info,
        ig.ingredient_name,
        m.category,
        m.image_url,
        m.price,
        oi.order_item_id,
        oi.orderitem_status
    FROM 
        ORDERS o
    LEFT JOIN 
        ORDER_ITEM oi ON o.order_id = oi.order_id
    LEFT JOIN 
        ORDER_INGREDIENT ig ON oi.order_item_id = ig.order_item_id
    LEFT JOIN
        MENU m ON oi.menu_name = m.name
    WHERE 
        o.order_id = %s
    """

    result = fetch_query(query, (id,))

    order_info = {
        "order_id": result[0][0],
        "order_status": result[0][1],
        "order_datetime": result[0][2].strftime("%Y-%m-%d %H:%M:%S"),
        "total_amount": float(result[0][3]),
        "table_number": result[0][4]
    }

    menus = []
    current_item_id = None
    current_item = None

    for row in result:
        order_item_id = row[5]
        
        # Check if we are starting a new menu item
        if current_item_id != order_item_id:
            if current_item:  # Save the previous menu item before creating a new one
                menus.append(current_item)
            
            current_item = {
                "menu": {
                    "name": row[6],
                    "category": row[11],
                    "image_url": row[12],
                    "price": float(row[13])
                },
                "order_item_id": row[14],
                "quantity": int(row[7]),
                "ingredients": [],
                "portion": row[8],
                "extraInfo": row[9],
                "orderitem_status": row[15],
                "order_price": (float(row[13]) + (10 if row[8] == "พิเศษ" else 0)) * int(row[7])
            }
            current_item_id = order_item_id
        
        # Add ingredient to the current menu item
        if row[10]:  # Check if ingredient_name is not None
            current_item["ingredients"].append(row[10])

    if current_item:  # Don't forget to add the last item
        menus.append(current_item)

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

    socketio.emit('update_order', {"order_id": order_id, "order_status": order_status})
    return jsonify({"code": "success", "message": "Order updated successfully."})


@orders_blueprint.route('/orders/delete', methods=['DELETE'])
def delete_order():
    data = request.get_json()
    order_id = data.get("order_id")

    if not order_id:
        raise ValueError("Missing required fields.")
    
    if not validate_uuid(order_id):
        raise ValueError("Invalid order ID.")
    
    if not isOrderExist(order_id):
        raise ValueError("Order does not exist.")
    
    query = """
    DELETE FROM ORDERS WHERE order_id = %s;

    DELETE FROM ORDER_ITEM WHERE order_id = %s;

    DELETE FROM ORDER_INGREDIENT WHERE order_item_id IN (
        SELECT order_item_id FROM ORDER_ITEM WHERE order_id = %s
    );
    """
    execute_command(query, (order_id, order_id, order_id))

    return jsonify({"code": "success", "message": "Order deleted successfully."})


@orders_blueprint.route('/orders/update-item-status', methods=['PUT'])
def update_status_order_item():
    data = request.get_json()
    order_item_id = data.get("order_item_id")
    order_item_status = data.get("order_item_status")

    if not all([order_item_id, order_item_status]):
        raise ValueError("Missing required fields.")
    
    query = "UPDATE ORDER_ITEM SET orderitem_status = %s WHERE order_item_id = %s"
    execute_command(query, (order_item_status, order_item_id))

    return jsonify({"code": "success", "message": "Order item updated successfully."})

def isOrderItemExist(order_item_id):
    """Check for duplicate order items."""
    query = "SELECT * FROM ORDER_ITEM WHERE order_item_id = %s"
    
    result = fetch_query(query, (order_item_id,))

    return len(result) > 0


@orders_blueprint.route('/orders/update-item', methods=['PUT'])
def update_order_item():
    data = request.get_json()
    order_item_id = data.get("order_item_id")
    ingredients = data.get("ingredients")
    portion = data.get("portion")
    extra_info = data.get("extraInfo")

    if not all([order_item_id]):
        raise ValueError("Missing required fields.")
    
    if not (ingredients or portion or extra_info):
        raise ValueError("No data provided to update.")
    
    if not validate_uuid(order_item_id):
        raise ValueError("Invalid order item ID.")
    
    if not isOrderItemExist(order_item_id):
        raise ValueError("Order item does not exist.")
    
    validate_order_item([{
        "menu": {"name": fetch_query("SELECT menu_name FROM ORDER_ITEM WHERE order_item_id = %s", (order_item_id,))[0][0]},
        "quantity": 1,
        "ingredients": ingredients,
        "portion": portion,
        "extraInfo": extra_info
    }])
    
    if ingredients:
        query = "DELETE FROM ORDER_INGREDIENT WHERE order_item_id = %s"
        execute_command(query, (order_item_id,))
        
        for ingredient in ingredients:
            query = "INSERT INTO ORDER_INGREDIENT (order_item_id, ingredient_name) VALUES (%s, %s)"
            execute_command(query, (order_item_id, ingredient))

    if portion:
        query = "UPDATE ORDER_ITEM SET portions = %s WHERE order_item_id = %s"
        execute_command(query, (portion, order_item_id))

    if extra_info:
        query = "UPDATE ORDER_ITEM SET extra_info = %s WHERE order_item_id = %s"
        execute_command(query, (extra_info, order_item_id))

    return jsonify({"code": "success", "message": "Order item updated successfully."})

@orders_blueprint.route('/orders/delete-item', methods=['DELETE'])
def delete_order_item():
    data = request.get_json()
    order_item_id = data.get("order_item_id")

    if not order_item_id:
        raise ValueError("Missing required fields.")
    
    if not validate_uuid(order_item_id):
        raise ValueError("Invalid order item ID.")
    
    if not isOrderItemExist(order_item_id):
        raise ValueError("Order item does not exist.")
    
    query = """
    DELETE FROM ORDER_ITEM WHERE order_item_id = %s;

    DELETE FROM ORDER_INGREDIENT WHERE order_item_id = %s;
    """
    execute_command(query, (order_item_id, order_item_id))

    return jsonify({"code": "success", "message": "Order item deleted successfully."})

@orders_blueprint.route('/orders/items', methods=['GET'])
def get_order_item():
    orderitem_status = request.args.get("status")

    query = """
    SELECT 
        oi.order_item_id,
        oi.menu_name,
        oi.quantity,
        oi.portions,
        oi.extra_info,
        oi.orderitem_status,
        m.category,
        m.image_url,
        m.price,
        o.order_id,
        o.order_datetime,
        o.table_number
    FROM
        ORDER_ITEM oi
    LEFT JOIN
        MENU m ON oi.menu_name = m.name
    LEFT JOIN
        ORDERS o ON oi.order_id = o.order_id
    """

    conditions = []
    params = []

    if orderitem_status:
        conditions.append("oi.orderitem_status = %s")
        params.append(orderitem_status)
    
    if conditions:
        query += " WHERE " + " AND ".join(conditions)

    result = fetch_query(query, tuple(params))

    order_items = [{
        "order_item_id": item[0],
        "menu": {
            "name": item[1],
            "category": item[6],
            "image_url": item[7],
            "price": float(item[8])
        },
        "quantity": int(item[2]),
        "portions": item[3],
        "extraInfo": item[4],
        "orderitem_status": item[5],
        "order_id": item[9],
        "order_datetime": item[10].strftime("%Y-%m-%d %H:%M:%S"),
        "table_number": item[11]
    } for item in result]

    return jsonify({"code": "success", "order_items": order_items})
    





