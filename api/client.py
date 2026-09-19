import json
import mimetypes
import threading
import urllib.error
import urllib.parse
import urllib.request

from kivy.clock import Clock

API_BASE_URL = "https://digishop-grwo.onrender.com/api"

_access_token = None
_refresh_token = None
_current_customer = None
_current_seller = None
_refresh_lock = threading.Lock()


class SimpleResponse:
    """Mimics the small subset of the requests.Response interface this app uses."""

    def __init__(self, status_code, body_bytes):
        self.status_code = status_code
        self._body_bytes = body_bytes or b""

    def json(self):
        if not self._body_bytes:
            return {}
        return json.loads(self._body_bytes.decode("utf-8"))


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


def _headers(multipart=False, content_type=None):
    headers = {}
    if content_type:
        headers["Content-Type"] = content_type
    elif not multipart:
        headers["Content-Type"] = "application/json"
    if _access_token:
        headers["Authorization"] = f"Bearer {_access_token}"
    return headers


def _do_request(method, url, headers=None, body=None, timeout=15):
    """Low-level blocking request built on urllib. Returns SimpleResponse or raises."""
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return SimpleResponse(resp.status, resp.read())
    except urllib.error.HTTPError as e:
        # HTTPError is raised for any 4xx/5xx; we still want the body + status code.
        return SimpleResponse(e.code, e.read())
    except urllib.error.URLError:
        # DNS failure, connection refused, timeout, etc.
        raise


def _build_multipart(data, files):
    """Builds a multipart/form-data body. files: dict of {field_name: file_object}."""
    boundary = "----DigiShopBoundary7f3a9c2e"
    lines = []

    for key, value in (data or {}).items():
        lines.append(f"--{boundary}".encode())
        lines.append(f'Content-Disposition: form-data; name="{key}"'.encode())
        lines.append(b"")
        lines.append(str(value).encode("utf-8"))

    for key, file_obj in (files or {}).items():
        filename = getattr(file_obj, "name", "upload").split("/")[-1].split("\\")[-1]
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        file_obj.seek(0)
        file_bytes = file_obj.read()
        lines.append(f"--{boundary}".encode())
        lines.append(
            f'Content-Disposition: form-data; name="{key}"; filename="{filename}"'.encode()
        )
        lines.append(f"Content-Type: {content_type}".encode())
        lines.append(b"")
        lines.append(file_bytes)

    lines.append(f"--{boundary}--".encode())
    lines.append(b"")

    body = b"\r\n".join(lines)
    content_type_header = f"multipart/form-data; boundary={boundary}"
    return body, content_type_header


def _try_refresh_token():
    global _access_token

    if not _refresh_token:
        return False

    with _refresh_lock:
        try:
            body = json.dumps({"refresh": _refresh_token}).encode("utf-8")
            response = _do_request(
                "POST",
                f"{API_BASE_URL}/accounts/token/refresh/",
                headers={"Content-Type": "application/json"},
                body=body,
            )
        except urllib.error.URLError:
            return False

        if response.status_code != 200:
            clear_session()
            return False

        _access_token = response.json().get("access")
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
        url = f"{API_BASE_URL}{path}"
        if params:
            query = "&".join(
                f"{k}={urllib.parse.quote(str(v))}"
                for k, v in params.items() if v is not None
            )
            if query:
                url = f"{url}?{query}"
        return _do_request("GET", url, headers=_headers())
    _run_async(do_request, callback)


def post_async(path, callback, data=None, files=None):
    def do_request():
        url = f"{API_BASE_URL}{path}"
        if files:
            body, content_type = _build_multipart(data, files)
            headers = _headers(multipart=True, content_type=content_type)
            return _do_request("POST", url, headers=headers, body=body, timeout=30)
        body = json.dumps(data or {}).encode("utf-8")
        return _do_request("POST", url, headers=_headers(), body=body)
    # A consumed file handle can't be safely resent, so skip the retry for uploads.
    _run_async(do_request, callback, retry_on_401=(files is None))


def patch_async(path, callback, data=None):
    def do_request():
        body = json.dumps(data or {}).encode("utf-8")
        return _do_request("PATCH", f"{API_BASE_URL}{path}", headers=_headers(), body=body)
    _run_async(do_request, callback)


def delete_async(path, callback):
    def do_request():
        return _do_request("DELETE", f"{API_BASE_URL}{path}", headers=_headers())
    _run_async(do_request, callback)
