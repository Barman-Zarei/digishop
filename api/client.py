import threading

import requests
from kivy.clock import Clock

API_BASE_URL = "https://digishop-grwo.onrender.com/api"

_access_token = None
_refresh_token = None
_current_customer = None
_current_seller = None
_refresh_lock = threading.Lock()


def set_session(tokens, customer=None, seller=None):
    global _access_token, _refresh_token, _current_customer, _current_seller
    _access_token = tokens["access"]
    _refresh_token = tokens["refresh"]
    _current_customer = customer
    _current_seller = seller


def set_seller(seller):
    global _current_seller
    _current_seller = seller


def clear_session():
    global _access_token, _refresh_token, _current_customer, _current_seller
    _access_token = None
    _refresh_token = None
    _current_customer = None
    _current_seller = None


def is_logged_in():
    return _access_token is not None


def is_seller():
    return _current_seller is not None


def get_current_customer():
    return _current_customer


def get_current_seller():
    return _current_seller


def safe_json(response):
    """Never raises. Returns dict with a readable 'error' key on any parse failure."""
    if response is None:
        return {"error": "No response from server"}
    try:
        return response.json()
    except ValueError:
        return {"error": f"Unexpected server response (status {response.status_code})"}


def _headers(multipart=False):
    headers = {}
    if not multipart:
        headers["Content-Type"] = "application/json"
    if _access_token:
        headers["Authorization"] = f"Bearer {_access_token}"
    return headers


def _try_refresh_token():
    global _access_token
    if not _refresh_token:
        return False

    with _refresh_lock:
        try:
            response = requests.post(
                f"{API_BASE_URL}/accounts/token/refresh/",
                json={"refresh": _refresh_token},
                timeout=30
            )
        except requests.RequestException:
            return False

        if response.status_code == 401:
            # Only a definitive "refresh token invalid/expired" should log the user out.
            clear_session()
            return False
        if response.status_code != 200:
            # Transient error (502, timeout, cold start) — keep the session, just fail this attempt.
            return False

        data = safe_json(response)
        _access_token = data.get("access")
        return _access_token is not None


def _run_async(request_func, callback, retry_on_401=True):
    def worker():
        try:
            response = request_func()
            if retry_on_401 and response is not None and response.status_code == 401 and _refresh_token:
                if _try_refresh_token():
                    response = request_func()
            error = None
        except Exception as e:
            response = None
            error = e

        if callback:
            Clock.schedule_once(lambda dt: callback(response, error))

    threading.Thread(target=worker, daemon=True).start()


def get_async(path, callback, params=None):
    def do_request():
        return requests.get(f"{API_BASE_URL}{path}", headers=_headers(), params=params, timeout=30)
    _run_async(do_request, callback)


def post_async(path, callback, data=None, files=None):
    def do_request():
        if files:
            return requests.post(f"{API_BASE_URL}{path}", headers=_headers(multipart=True), data=data, files=files, timeout=45)
        return requests.post(f"{API_BASE_URL}{path}", headers=_headers(), json=data, timeout=30)
    _run_async(do_request, callback, retry_on_401=True)


def patch_async(path, callback, data=None):
    def do_request():
        return requests.patch(f"{API_BASE_URL}{path}", headers=_headers(), json=data, timeout=30)
    _run_async(do_request, callback)


def delete_async(path, callback):
    def do_request():
        return requests.delete(f"{API_BASE_URL}{path}", headers=_headers(), timeout=30)
    _run_async(do_request, callback)
