from werkzeug.exceptions import HTTPException
from flask import jsonify
from app import create_app, socketio

app = create_app()

@app.errorhandler(HTTPException)
def handle_http_exception(error):
    response = error.get_response()
    response.data = jsonify({
        "code": error.code,
        "name": error.name,
        "description": error.description,
    }).get_data(as_text=True)
    response.content_type = "application/json"
    return response

@app.errorhandler(Exception)
def handle_exception(error):
    print(f"An error occurred: {str(error)}")
    
    if isinstance(error, ValueError):
        return jsonify({
            "code": "Bad Request", "message": str(error)}), 400
    
    return jsonify({
        "code": "Internal Server Error", "message": "An error occurred. Please try again later."
    }), 500


print(f"Running app on port {app.config['PORT']}...")
socketio.run(app, port=app.config['PORT'], debug=False)
