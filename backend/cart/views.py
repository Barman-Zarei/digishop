from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import transaction

from products.models import Product
from .models import CartItem
from .serializers import CartItemSerializer, CartItemCreateSerializer, CartItemUpdateSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def cart_list_view(request):
    customer = request.user.customer
    items = CartItem.objects.filter(customer=customer).select_related("product", "seller")
    serializer = CartItemSerializer(items, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def cart_add_view(request):
    customer = request.user.customer

    serializer = CartItemCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    requested_quantity = serializer.validated_data["quantity"]

    with transaction.atomic():
        try:
            product = Product.objects.select_for_update().get(
                id=serializer.validated_data["product_id"], is_active=True
            )
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

        existing_item = CartItem.objects.filter(customer=customer, product=product).first()
        already_in_cart = existing_item.quantity if existing_item else 0
        total_requested = already_in_cart + requested_quantity

        if total_requested > product.stock_quantity:
            return Response(
                {"error": f"Only {product.stock_quantity} in stock ({already_in_cart} already in your cart)"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if existing_item:
            existing_item.quantity = total_requested
            existing_item.save()
            cart_item = existing_item
        else:
            cart_item = CartItem.objects.create(
                customer=customer,
                product=product,
                seller=product.seller,
                quantity=requested_quantity
            )

    return Response(CartItemSerializer(cart_item, context={"request": request}).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def cart_update_view(request, item_id):
    customer = request.user.customer

    serializer = CartItemUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_quantity = serializer.validated_data["quantity"]

    with transaction.atomic():
        try:
            cart_item = CartItem.objects.select_related("product").select_for_update().get(
                id=item_id, customer=customer
            )
        except CartItem.DoesNotExist:
            return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

        if new_quantity > cart_item.product.stock_quantity:
            return Response(
                {"error": f"Only {cart_item.product.stock_quantity} in stock"},
                status=status.HTTP_400_BAD_REQUEST
            )

        cart_item.quantity = new_quantity
        cart_item.save()

    return Response(CartItemSerializer(cart_item, context={"request": request}).data)


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
