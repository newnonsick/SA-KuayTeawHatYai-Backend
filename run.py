from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    print(f"Running app on port {app.config['PORT']}...")
    socketio.run(app, port=app.config['PORT'], debug=False, host='0.0.0.0')
