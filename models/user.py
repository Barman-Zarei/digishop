from api import client


class User:
    @staticmethod
    def register(username, password, full_name, email, phone, address, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error)}, 0)
                return
            data = response.json()
            if response.status_code == 201:
                client.set_session(data["tokens"], customer=data.get("customer"))
            callback(data, response.status_code)

        client.post_async("/accounts/register/", on_response, data={
            "username": username, "password": password, "full_name": full_name,
            "email": email or "", "phone": phone or "", "address": address or ""
        })

    @staticmethod
    def login(username, password, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error)}, 0)
                return
            data = response.json()
            if response.status_code == 200:
                client.set_session(
                    data["tokens"], customer=data.get("customer"), seller=data.get("seller")
                )
            callback(data, response.status_code)

        client.post_async("/accounts/login/", on_response, data={
            "username": username, "password": password
        })

    @staticmethod
    def become_seller(store_name, phone, national_id, legal_full_name, bank_account_number, callback):
        def on_response(response, error):
            if error or response is None:
                callback({"error": str(error) if error else "No response from server"}, 0)
                return
            callback(response.json(), response.status_code)

        client.post_async("/accounts/become-seller/", on_response, data={
            "store_name": store_name,
            "phone": phone,
            "national_id": national_id,
            "legal_full_name": legal_full_name,
            "bank_account_number": bank_account_number,
        })

    @staticmethod
    def logout():
        client.clear_session()
