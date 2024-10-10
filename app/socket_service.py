from flask_socketio import emit
from . import socketio

@socketio.on('connect')
def handle_connect():
    emit('response', {'message': 'Connected to server'})

@socketio.on('my_event')
def handle_my_custom_event(json):
    print(f'Received data: {json}')
    emit('response', {'message': 'Received your data'})
