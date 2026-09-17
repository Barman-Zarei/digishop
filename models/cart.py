from api import client


class CartItem:
    @staticmethod
    def get_cart(callback):
        def on_response(response, error):
            if error:
                callback([], "Network error — check your connection")
                return
            if response is None or response.status_code != 200:
                callback([], "Could not load your cart")
                return
            callback(response.json(), None)

        client.get_async("/cart/", on_response)

    @staticmethod
    def add(product_id, quantity, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            callback(response.json(), response.status_code)

        client.post_async("/cart/add/", on_response, data={
            "product_id": product_id, "quantity": quantity
        })

    @staticmethod
    def update_quantity(item_id, quantity, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            callback(response.json(), response.status_code)

        client.patch_async(f"/cart/{item_id}/", on_response, data={"quantity": quantity})

    @staticmethod
    def remove(item_id, callback):
        def on_response(response, error):
            callback(response is not None and response.status_code == 204)

        client.delete_async(f"/cart/{item_id}/remove/", on_response)
