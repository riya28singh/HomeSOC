
import mysql.connector
from mysql.connector import Error
import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration
DB_TYPE = os.getenv("DB_TYPE", "sqlite") # 'mysql' or 'sqlite'
DB_NAME = os.getenv("DB_NAME", "soc_db")

def get_db_connection():
    """Establishes a connection to the database (MySQL or SQLite)."""
    if DB_TYPE == 'sqlite':
        try:
            # SQLite connection
            base_dir = os.path.dirname(os.path.abspath(__file__))
            db_path = os.path.join(base_dir, f"{DB_NAME}.sqlite")
            conn = sqlite3.connect(db_path, check_same_thread=False)
            conn.row_factory = sqlite3.Row # Access columns by name
            return conn
        except Exception as e:
            print(f"Error connecting to SQLite: {e}")
            return None
    
    else:
        # MySQL connection
        try:
            connection = mysql.connector.connect(
                host=os.getenv("DB_HOST", "localhost"),
                user=os.getenv("DB_USER", "root"),
                password=os.getenv("DB_PASSWORD", ""),
                database=DB_NAME
            )
            if connection.is_connected():
                return connection
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return None

def init_db():
    """Initializes the database using the appropriate schema."""
    conn = get_db_connection()
    if conn is None:
        print("Could not connect to database to initialize schema.")
        return

    cursor = conn.cursor()
    
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        if DB_TYPE == 'sqlite':
            schema_file = os.path.join(base_dir, 'schema_sqlite.sql')
            print(f"Initializing SQLite database using {schema_file}...")
            # SQLite executes script directly
            with open(schema_file, 'r') as f:
                cursor.executescript(f.read())
        else:
            schema_file = os.path.join(base_dir, 'schema.sql')
            print(f"Initializing MySQL database using {schema_file}...")
            with open(schema_file, 'r') as f:
                schema_sql = f.read()
            # MySQL multi-statement execution
            for result in cursor.execute(schema_sql, multi=True):
                pass
        
        conn.commit()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Failed to init DB: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    init_db()
