import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('POSTGRES_HOST', 'localhost')
DB_PORT = os.getenv('POSTGRES_PORT', 5432)

print(f"Connecting to database {DB_NAME} on {DB_HOST}:{DB_PORT} as {DB_USER}...")

conn = psycopg2.connect(
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
)
conn.autocommit = True
cursor = conn.cursor()

def run_migration(script_path):
    with open(script_path, 'r') as file:
        sql_script = file.read()

    cursor.execute(sql_script)
    print(f"Migration {script_path} executed successfully.")

def apply_migrations():
    migration_folder = 'migrations'

    for filename in sorted(os.listdir(migration_folder)):
        if filename.endswith('.sql'):
            script_path = os.path.join(migration_folder, filename)
            run_migration(script_path)

def main():
    print("Starting migrations...")

    apply_migrations()

    cursor.close()
    conn.close()

    print("Migrations completed.")

if __name__ == "__main__":
    main()
