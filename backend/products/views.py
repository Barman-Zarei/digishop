from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer

import math

from accounts.utils import get_seller_or_error

from accounts.utils import get_seller_or_error
from .serializers import ProductCreateSerializer  # اگه از قبل ایمپورت نکردی


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def product_create_view(request):
    seller, error = get_seller_or_error(request)
    if error:
        return error
    serializer = ProductCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    product = serializer.save(seller=seller)
    return Response(ProductSerializer(product, context={"request": request}).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    return Response(ProductSerializer(product, context={"request": request}).data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_product_list_view(request):
    seller, error = get_seller_or_error(request)
    if error:
        return error
    products = Product.objects.filter(seller=seller).order_by("-created_at")
    return Response(ProductSerializer(products, many=True, context={"request": request}).data)

def _parse_price(value):
    if value is None:
        return None
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return "invalid"
    if not math.isfinite(parsed) or parsed < 0 or parsed > 10 ** 14:
        return "invalid"
    return parsed


@api_view(["GET"])
@permission_classes([AllowAny])
def product_list_view(request):
    products = Product.objects.filter(is_active=True).order_by("-created_at")

    search = request.query_params.get("search")
    if search:
        products = products.filter(name__icontains=search)

    if request.query_params.get("min_price"):
        min_price = _parse_price(request.query_params.get("min_price"))
        if min_price == "invalid":
            return Response({"error": "min_price must be a valid non-negative number"}, status=status.HTTP_400_BAD_REQUEST)
        products = products.filter(price__gte=min_price)

    if request.query_params.get("max_price"):
        max_price = _parse_price(request.query_params.get("max_price"))
        if max_price == "invalid":
            return Response({"error": "max_price must be a valid non-negative number"}, status=status.HTTP_400_BAD_REQUEST)
        products = products.filter(price__lt=max_price)

    return Response(ProductSerializer(products, many=True, context={"request": request}).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def product_update_view(request, product_id):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)
    try:
        product = Product.objects.get(id=product_id, seller=request.user.seller, is_active=True)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = ProductUpdateSerializer(product, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(ProductSerializer(product, context={"request": request}).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def product_delete_view(request, product_id):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)
    try:
        product = Product.objects.get(id=product_id, seller=request.user.seller)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)
    product.is_active = False
    product.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
