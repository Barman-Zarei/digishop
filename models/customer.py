from db.connection import get_connection


class Customer:
    @staticmethod
    def create(user_id, full_name, address=None, phone=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = (
                "INSERT INTO customers (user_id, full_name, address, phone) "
                "VALUES (%s, %s, %s, %s)"
            )
            values = (user_id, full_name, address, phone)
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_id(customer_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM customers WHERE id = %s"
            cursor.execute(query, (customer_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_user_id(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM customers WHERE user_id = %s"
            cursor.execute(query, (user_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
