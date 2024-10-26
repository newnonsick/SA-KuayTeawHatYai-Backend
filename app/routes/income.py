from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query
import datetime

income_blueprint = Blueprint('income', __name__)

@income_blueprint.route('/income', methods=['GET'])
def get_income():
    date = request.args.get('date')

    if date:
    
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format. Use YYYY-MM-DD.")

        query = """
            SELECT m.category, SUM(oi.price * oi.quantity) AS total_income
            FROM MENU m
            JOIN ORDER_ITEM oi ON m.name = oi.menu_name
            JOIN ORDERS o ON oi.order_id = o.order_id
            WHERE o.order_datetime::date = %s
            GROUP BY m.category
        """

        result = fetch_query(query, (date,))

        income = [{
            "category": item[0],
            "total_income": float(item[1])
        } for item in result]

        return jsonify({"code": "success", "income": income, "total_income": sum([item["total_income"] for item in income])})
    
    else:

        query = """
            SELECT m.category, SUM(oi.price * oi.quantity) AS total_income
            FROM MENU m
            JOIN ORDER_ITEM oi ON m.name = oi.menu_name
            JOIN ORDERS o ON oi.order_id = o.order_id
            GROUP BY m.category
        """

        result = fetch_query(query)

        income = [{
            "category": item[0],
            "total_income": float(item[1])
        } for item in result]

        return jsonify({"code": "success", "income": income, "total_income": sum([item["total_income"] for item in income])})