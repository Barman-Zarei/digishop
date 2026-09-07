from db.connection import get_connection


class Seller:
    @staticmethod
    def create(user_id, store_name, phone=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = (
                "INSERT INTO sellers (user_id, store_name, phone) "
                "VALUES (%s, %s, %s)"
            )
            values = (user_id, store_name, phone)
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_id(seller_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM sellers WHERE id = %s"
            cursor.execute(query, (seller_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM sellers WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
