import sqlite3
import os

# Path to your SQLite database and SQL script
db_path = "database.db"  # Or use an environment variable to specify the database path
sql_file_path = "create.sql"  # Ensure your create.sql is in the correct path

# Function to run the SQL script
def run_create_sql():
    if os.path.exists(sql_file_path):
        with open(sql_file_path, 'r') as file:
            sql_script = file.read()

        connection = sqlite3.connect(db_path)
        cursor = connection.cursor()

        try:
            cursor.executescript(sql_script)
            connection.commit()
            print("Database setup completed.")
        except Exception as e:
            print(f"Error executing SQL script: {e}")
        finally:
            connection.close()

if __name__ == "__main__":
    run_create_sql()
