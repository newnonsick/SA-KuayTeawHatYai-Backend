import psycopg2
from flask import current_app

def init_db(app):
    app.db_connection = psycopg2.connect(
        user=app.config['POSTGRES_USER'],
        password=app.config['POSTGRES_PASSWORD'],
        host=app.config['POSTGRES_HOST'],
        port=app.config['POSTGRES_PORT'],
        database=app.config['POSTGRES_DB']
    )

#use with INSERT, UPDATE, DELETE queries
def execute_command(query, params=None):
    conn = current_app.db_connection
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
        print(f"Error executing command: {e}")
        conn.rollback()
        result = "error"
    finally:
        cursor.close()

    return result

#use with SELECT queries
def fetch_query(query, params=None):
    conn = current_app.db_connection
    cursor = conn.cursor()
    result = None
    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        result = cursor.fetchall()
    except Exception as e:
        print(f"Error fetching query: {e}")
        result = "error"
    finally:
        cursor.close()

    return result



