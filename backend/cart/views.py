from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from products.models import Product
from .models import CartItem
from .serializers import CartItemSerializer, CartItemCreateSerializer, CartItemUpdateSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cart_list_view(request):
    customer = request.user.customer
    items = CartItem.objects.filter(customer=customer)
    serializer = CartItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cart_add_view(request):
    customer = request.user.customer

    serializer = CartItemCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        product = Product.objects.get(id=serializer.validated_data["product_id"])
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    cart_item = CartItem.objects.create(
        customer=customer,
        product=product,
        seller=product.seller,
        quantity=serializer.validated_data["quantity"]
    )

    return Response(CartItemSerializer(cart_item).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cart_update_view(request, item_id):
    customer = request.user.customer

    try:
        cart_item = CartItem.objects.get(id=item_id, customer=customer)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = CartItemUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    cart_item.quantity = serializer.validated_data["quantity"]
    cart_item.save()

    return Response(CartItemSerializer(cart_item).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def cart_remove_view(request, item_id):
    customer = request.user.customer

    try:
        cart_item = CartItem.objects.get(id=item_id, customer=customer)
    except CartItem.DoesNotExist:
        return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    cart_item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
