import psycopg2
from psycopg2 import OperationalError
from flask import current_app
import atexit

def init_db(app):
    """Initialize the database connection and store it in the app object."""
    app.db_connection = psycopg2.connect(
        user=app.config['POSTGRES_USER'],
        password=app.config['POSTGRES_PASSWORD'],
        host=app.config['POSTGRES_HOST'],
        port=app.config['POSTGRES_PORT'],
        database=app.config['POSTGRES_DB']
    )
    
    atexit.register(close_db_connection, app)

def close_db_connection(app):
    """Close the database connection when the app shuts down."""
    conn = app.db_connection
    if conn:
        conn.close()
        print("Database connection closed.")

def get_db_connection():
    """Ensure the database connection is open before use."""
    conn = current_app.db_connection

    try:
        conn.cursor().execute('SELECT 1')
    except OperationalError:
        print("Connection was closed, reopening...")
        conn = psycopg2.connect(
            user=current_app.config['POSTGRES_USER'],
            password=current_app.config['POSTGRES_PASSWORD'],
            host=current_app.config['POSTGRES_HOST'],
            port=current_app.config['POSTGRES_PORT'],
            database=current_app.config['POSTGRES_DB']
        )
        current_app.db_connection = conn

    return conn

# Use with INSERT, UPDATE, DELETE queries
def execute_command(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        conn.commit()
        result = "success"
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()

    return result

# Use with SELECT queries
def fetch_query(query, params=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = cursor.fetchall()
    except Exception as e:
        raise e
    finally:
        cursor.close()

    return result
