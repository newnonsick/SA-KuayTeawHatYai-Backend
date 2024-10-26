from flask import Blueprint, jsonify, request
from ..db import execute_command, fetch_query

search_blueprint = Blueprint('search', __name__)

