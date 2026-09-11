from collections import defaultdict

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.db import transaction

from cart.models import CartItem
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderStatusUpdateSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_list_view(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by("-order_date")
    serializer = OrderSerializer(orders, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def order_create_view(request):
    customer = request.user.customer
    cart_items = CartItem.objects.filter(customer=customer)

    if not cart_items.exists():
        return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    items_by_seller = defaultdict(list)
    for item in cart_items:
        items_by_seller[item.seller_id].append(item)

    created_orders = []

    with transaction.atomic():
        for seller_id, items in items_by_seller.items():
            total_amount = sum(item.product.price * item.quantity for item in items)

            order = Order.objects.create(
                customer=customer,
                seller_id=seller_id,
                total_amount=total_amount,
                status="pending"
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price
                )

            created_orders.append(order)

        cart_items.delete()

    serializer = OrderSerializer(created_orders, many=True, context={"request": request})
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_order_list_view(request):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)

    seller = request.user.seller
    orders = Order.objects.filter(seller=seller).order_by("-order_date")
    serializer = OrderSerializer(orders, many=True, context={"request": request})
    return Response(serializer.data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def order_update_status_view(request, order_id):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = Order.objects.get(id=order_id, seller=request.user.seller)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = OrderStatusUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    order.status = serializer.validated_data["status"]
    order.save()

    return Response(OrderSerializer(order, context={"request": request}).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def order_delete_view(request, order_id):
    if not hasattr(request.user, "seller"):
        return Response({"error": "You must be a seller"}, status=status.HTTP_403_FORBIDDEN)

    try:
        order = Order.objects.get(id=order_id, seller=request.user.seller)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    order.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
