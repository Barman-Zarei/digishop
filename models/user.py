from api import client


class User:
    @staticmethod
    def register(username, password, full_name, email="", phone="", address="", callback=None):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            data = client.safe_json(response)
            if response.status_code == 201:
                client.set_session(data["tokens"], customer=data.get("customer"))
            callback(data, response.status_code)
        client.post_async("/accounts/register/", on_response, data={
            "username": username, "password": password, "full_name": full_name,
            "email": email, "phone": phone, "address": address,
        })

    @staticmethod
    def login(username, password, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            data = client.safe_json(response)
            if response.status_code == 200:
                client.set_session(data["tokens"], customer=data.get("customer"), seller=data.get("seller"))
            callback(data, response.status_code)
        client.post_async("/accounts/login/", on_response, data={"username": username, "password": password})

    @staticmethod
    def become_seller(store_name, phone, national_id, legal_full_name, bank_account_number, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            data = client.safe_json(response)
            if response.status_code == 201:
                client.set_seller(data.get("seller"))
            callback(data, response.status_code)

        client.post_async("/accounts/become-seller/", on_response, data={
            "store_name": store_name, "phone": phone, "national_id": national_id,
            "legal_full_name": legal_full_name, "bank_account_number": bank_account_number,
        })

    @staticmethod
    def logout():
        client.clear_session()
