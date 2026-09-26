from rest_framework import status
from rest_framework.response import Response


def get_customer_or_error(request):
    if not hasattr(request.user, "customer"):
        return None, Response({"error": "This account has no customer profile"}, status=status.HTTP_400_BAD_REQUEST)
    return request.user.customer, None


def get_seller_or_error(request):
    if not hasattr(request.user, "seller"):
        return None, Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)
    return request.user.seller, None
