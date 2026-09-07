from db.connection import get_connection


class CartItem:
    @staticmethod
    def add(customer_id, product_id, seller_id, quantity):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = (
                "INSERT INTO cart_item (customer_id, product_id, seller_id, quantity) "
                "VALUES (%s, %s, %s, %s)"
            )
            values = (customer_id, product_id, seller_id, quantity)
            cursor.execute(query, values)
            conn.commit()
            return cursor.lastrowid
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_cart(customer_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = (
                "SELECT cart_item.id, cart_item.quantity, cart_item.seller_id, "
                "products.id AS product_id, products.name, products.price, products.image_path "
                "FROM cart_item "
                "JOIN products ON cart_item.product_id = products.id "
                "WHERE cart_item.customer_id = %s"
            )
            cursor.execute(query, (customer_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_quantity(cart_item_id, quantity):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = "UPDATE cart_item SET quantity = %s WHERE id = %s"
            cursor.execute(query, (quantity, cart_item_id))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def remove(cart_item_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM cart_item WHERE id = %s"
            cursor.execute(query, (cart_item_id,))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def clear(customer_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = "DELETE FROM cart_item WHERE customer_id = %s"
            cursor.execute(query, (customer_id,))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()
