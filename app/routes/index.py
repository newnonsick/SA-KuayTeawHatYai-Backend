from flask import Blueprint, jsonify

index_blueprint = Blueprint('index', __name__)

@index_blueprint.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Hello, World!"})


@index_blueprint.route('/test-emit', methods=['GET'])
def test_emit():
    from ..socket_service import socketio

    socketio.emit('response', {'message': 'Test emit from server'})

    return jsonify({"message": "Emitted event."})