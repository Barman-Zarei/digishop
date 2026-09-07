from db.connection import get_connection


class Order:
    @staticmethod
    def create(customer_id, seller_id, items):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            total_amount = sum(item["quantity"] * item["unit_price"] for item in items)

            order_query = (
                "INSERT INTO orders (customer_id, seller_id, total_amount, status) "
                "VALUES (%s, %s, %s, %s)"
            )
            cursor.execute(order_query, (customer_id, seller_id, total_amount, "pending"))
            order_id = cursor.lastrowid

            item_query = (
                "INSERT INTO order_item (order_id, product_id, quantity, unit_price) "
                "VALUES (%s, %s, %s, %s)"
            )
            for item in items:
                cursor.execute(
                    item_query,
                    (order_id, item["product_id"], item["quantity"], item["unit_price"])
                )

            conn.commit()
            return order_id
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_customer(customer_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM orders WHERE customer_id = %s ORDER BY order_date DESC"
            cursor.execute(query, (customer_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_seller(seller_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM orders WHERE seller_id = %s ORDER BY order_date DESC"
            cursor.execute(query, (seller_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_items(order_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = (
                "SELECT order_item.id, order_item.quantity, order_item.unit_price, "
                "products.id AS product_id, products.name, products.image_path "
                "FROM order_item "
                "JOIN products ON order_item.product_id = products.id "
                "WHERE order_item.order_id = %s"
            )
            cursor.execute(query, (order_id,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def update_status(order_id, new_status):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            query = "UPDATE orders SET status = %s WHERE id = %s"
            cursor.execute(query, (new_status, order_id))
            conn.commit()
            return cursor.rowcount
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def get_by_id(order_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            query = "SELECT * FROM orders WHERE id = %s"
            cursor.execute(query, (order_id,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conn.close()
