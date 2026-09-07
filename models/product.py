from db.connection import get_connection


class Product:
    @staticmethod
    def create(seller_id, name, price, stock_quantity, description=None, image_path=None):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = (
                "INSERT INTO products (seller_id, name, description, price, stock_quantity, image_path) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            values = (seller_id, name, description, price, stock_quantity, image_path)
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_id(product_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_all():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM products"
            cursor.execute(query)
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_seller(seller_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM products WHERE seller_id = %s"
            cursor.execute(query, (seller_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_stock(product_id, new_quantity):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = "UPDATE products SET stock_quantity = %s WHERE id = %s"
            cursor.execute(query, (new_quantity, product_id))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def delete(product_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM products WHERE id = %s"
            cursor.execute(query, (product_id,))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()
