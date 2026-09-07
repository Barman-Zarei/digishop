import bcrypt
from db.connection import get_connection


class User:
    @staticmethod
    def create(username, password, email, phone=None):
        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())

        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = (
                "INSERT INTO users (username, password_hash, email, phone) "
                "VALUES (%s, %s, %s, %s)"
            )
            values = (username, password_hash, email, phone)
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_username(username):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM users WHERE id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def authenticate(username, password):
        user = User.get_by_username(username)
        if user is None:
            return None

        stored_hash = user["password_hash"]
        if isinstance(stored_hash, str):
            stored_hash = stored_hash.encode()

        if bcrypt.checkpw(password.encode(), stored_hash):
            return user
        return None
