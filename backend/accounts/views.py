from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate

from .models import Customer, Seller
from .serializers import (
    RegisterSerializer,
    CustomerSerializer,
    SellerSerializer,
    BecomeSellerSerializer
)


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }


@api_view(["POST"])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    customer = serializer.save()

    tokens = get_tokens_for_user(customer.user)

    return Response({
        "message": "Registration successful",
        "tokens": tokens,
        "customer": CustomerSerializer(customer).data
    }, status=status.HTTP_201_CREATED)


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response(
            {"error": "Username and password are required"},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(username=username, password=password)

    if user is None:
        return Response(
            {"error": "Invalid username or password"},
            status=status.HTTP_401_UNAUTHORIZED
        )

    tokens = get_tokens_for_user(user)

    customer = Customer.objects.filter(user=user).first()
    seller = Seller.objects.filter(user=user).first()

    return Response({
        "message": "Login successful",
        "tokens": tokens,
        "customer": CustomerSerializer(customer).data if customer else None,
        "seller": SellerSerializer(seller).data if seller else None
    })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def become_seller_view(request):
    serializer = BecomeSellerSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    seller = serializer.save()

    return Response({
        "message": "You are now a seller",
        "seller": SellerSerializer(seller).data
    }, status=status.HTTP_201_CREATED)
