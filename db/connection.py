import mysql.connector
import os
import dotenv

dotenv.load_dotenv()

def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_DATABASE")
        )
    except mysql.connector.Error as e:
        print(f"Database connection error: {e}")
        raise
