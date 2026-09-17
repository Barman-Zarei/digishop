from api import client


class Order:
    @staticmethod
    def get_all(callback):
        def on_response(response, error):
            if error:
                callback([], "Network error — check your connection")
                return
            if response is None or response.status_code != 200:
                callback([], "Could not load your orders")
                return
            callback(response.json(), None)

        client.get_async("/orders/", on_response)

    @staticmethod
    def create(callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            callback(response.json(), response.status_code)

        client.post_async("/orders/create/", on_response)

    @staticmethod
    def get_seller_orders(callback):
        def on_response(response, error):
            if error:
                callback([], "Network error — check your connection")
                return
            if response is None or response.status_code != 200:
                callback([], "Could not load orders")
                return
            callback(response.json(), None)

        client.get_async("/orders/seller/", on_response)

    @staticmethod
    def update_status(order_id, new_status, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            callback(response.json(), response.status_code)

        client.patch_async(f"/orders/{order_id}/status/", on_response, data={"status": new_status})

    @staticmethod
    def delete(order_id, callback):
        def on_response(response, error):
            callback(response is not None and response.status_code == 204)

        client.delete_async(f"/orders/{order_id}/", on_response)
