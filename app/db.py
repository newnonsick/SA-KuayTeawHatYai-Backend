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

def execute_query(query, params=None):
    conn = current_app.db_connection
    cursor = conn.cursor()
    cursor.execute(query, params)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    return result

