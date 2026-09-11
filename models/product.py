from api import client


class Product:
    @staticmethod
    def get_all(callback, search=None, min_price=None, max_price=None):
        params = {}
        if search:
            params["search"] = search
        if min_price is not None:
            params["min_price"] = min_price
        if max_price is not None:
            params["max_price"] = max_price

        def on_response(response, error):
            if error or response is None or response.status_code != 200:
                callback([])
                return
            callback(response.json())

        client.get_async("/products/", on_response, params=params)

    @staticmethod
    def get_by_id(product_id, callback):
        def on_response(response, error):
            if error or response is None or response.status_code != 200:
                callback(None)
                return
            callback(response.json())

        client.get_async(f"/products/{product_id}/", on_response)

    @staticmethod
    def get_mine(callback):
        def on_response(response, error):
            if error or response is None or response.status_code != 200:
                callback([])
                return
            callback(response.json())

        client.get_async("/products/mine/", on_response)

    @staticmethod
    def create(name, price, stock_quantity, callback, description=None, image_file_path=None):
        data = {
            "name": name,
            "price": str(price),
            "stock_quantity": str(stock_quantity),
            "description": description or "",
        }

        files = None
        opened_file = None
        if image_file_path:
            opened_file = open(image_file_path, "rb")
            files = {"image": opened_file}

        def on_response(response, error):
            if opened_file:
                opened_file.close()
            if error or response is None:
                callback({"error": str(error)}, 0)
                return
            callback(response.json(), response.status_code)

        client.post_async("/products/create/", on_response, data=data, files=files)

    @staticmethod
    def update(product_id, callback, name=None, price=None, stock_quantity=None, description=None):
        data = {}
        if name is not None:
            data["name"] = name
        if price is not None:
            data["price"] = str(price)
        if stock_quantity is not None:
            data["stock_quantity"] = str(stock_quantity)
        if description is not None:
            data["description"] = description

        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error)}, 0)
                return
            callback(response.json(), response.status_code)

        client.patch_async(f"/products/{product_id}/update/", on_response, data=data)

    @staticmethod
    def delete(product_id, callback):
        def on_response(response, error):
            callback(response is not None and response.status_code == 204)

        client.delete_async(f"/products/{product_id}/delete/", on_response)
