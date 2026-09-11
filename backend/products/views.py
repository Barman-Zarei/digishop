from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Product
from .serializers import ProductSerializer, ProductCreateSerializer, ProductUpdateSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def product_list_view(request):
    products = Product.objects.all()

    search = request.query_params.get("search")
    if search:
        products = products.filter(name__icontains=search)

    min_price = request.query_params.get("min_price")
    if min_price:
        products = products.filter(price__gte=min_price)

    max_price = request.query_params.get("max_price")
    if max_price:
        products = products.filter(price__lt=max_price)

    serializer = ProductSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def product_detail_view(request, product_id):
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = ProductSerializer(product, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def product_create_view(request):
    if not hasattr(request.user, "seller"):
        return Response(
            {"error": "You must be a seller to add products"},
            status=status.HTTP_403_FORBIDDEN
        )

    serializer = ProductCreateSerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    product = serializer.save()

    return Response(
        ProductSerializer(product, context={"request": request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_product_list_view(request):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)

    products = Product.objects.filter(seller=request.user.seller)
    serializer = ProductSerializer(products, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def product_update_view(request, product_id):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)

    try:
        product = Product.objects.get(id=product_id, seller=request.user.seller)
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

    product.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
