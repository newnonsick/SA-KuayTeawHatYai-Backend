from flask_socketio import emit
from . import socketio

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('response', {'message': 'Connected to server'})


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

@socketio.on('my_event')
def handle_my_custom_event(json):
    print(f'Received data: {json}')
    emit('response', {'message': 'Received your data'})
