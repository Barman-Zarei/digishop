from rest_framework.views import exception_handler


def flatten_error(detail):
    """Turns DRF's nested error dict/list into a single readable string."""
    if isinstance(detail, dict):
        parts = []
        for key, value in detail.items():
            parts.append(f"{key}: {flatten_error(value)}")
        return "; ".join(parts)
    if isinstance(detail, list):
        return " ".join(flatten_error(item) for item in detail)
    return str(detail)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        response.data = {"error": flatten_error(response.data)}
    return response
