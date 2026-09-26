from collections import defaultdict

from cart.models import CartItem

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.utils import get_customer_or_error, get_seller_or_error
from products.models import Product
from .models import Order, OrderItem
from .serializers import OrderSerializer, OrderStatusUpdateSerializer


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def order_list_view(request):
    customer, error = get_customer_or_error(request)
    if error:
        return error
    orders = Order.objects.filter(customer=customer).order_by("-order_date")
    return Response(OrderSerializer(orders, many=True, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def order_create_view(request):
    customer, error = get_customer_or_error(request)
    if error:
        return error

    shipping_address = (request.data.get("shipping_address") or "").strip()
    shipping_phone = (request.data.get("shipping_phone") or "").strip()

    if len(shipping_address) < 5:
        return Response({"error": "Please enter a valid shipping address"}, status=status.HTTP_400_BAD_REQUEST)
    if len(shipping_phone) < 8:
        return Response({"error": "Please enter a valid phone number"}, status=status.HTTP_400_BAD_REQUEST)

    cart_items = CartItem.objects.filter(customer=customer, product__is_active=True).select_related("product")
    if not cart_items.exists():
        return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)

    items_by_seller = defaultdict(list)
    for item in cart_items:
        items_by_seller[item.seller_id].append(item)

    created_orders = []
    with transaction.atomic():
        product_ids = sorted(item.product_id for item in cart_items)
        locked_products = {
            p.id: p for p in Product.objects.select_for_update().filter(id__in=product_ids).order_by("id")
        }

        for item in cart_items:
            product = locked_products[item.product_id]
            if item.quantity > product.stock_quantity:
                return Response(
                    {"error": f"'{product.name}' only has {product.stock_quantity} in stock"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        for seller_id, items in items_by_seller.items():
            total_amount = sum(item.product.price * item.quantity for item in items)
            order = Order.objects.create(
                customer=customer, seller_id=seller_id, total_amount=total_amount,
                status="pending", shipping_address=shipping_address, shipping_phone=shipping_phone,
            )
            for item in items:
                product = locked_products[item.product_id]
                OrderItem.objects.create(
                    order=order, product=product, product_name=product.name,
                    quantity=item.quantity, unit_price=product.price
                )
                product.stock_quantity -= item.quantity
                product.save()
            created_orders.append(order)

        cart_items.delete()

    return Response(
        OrderSerializer(created_orders, many=True, context={"request": request}).data,
        status=status.HTTP_201_CREATED
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def seller_order_list_view(request):
    seller, error = get_seller_or_error(request)
    if error:
        return error
    orders = Order.objects.filter(seller=seller, hidden_from_seller=False).order_by("-order_date")
    return Response(OrderSerializer(orders, many=True, context={"request": request}).data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def order_update_status_view(request, order_id):
    seller, error = get_seller_or_error(request)
    if error:
        return error

    serializer = OrderStatusUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_status = serializer.validated_data["status"]

    with transaction.atomic():
        try:
            order = Order.objects.select_for_update().get(id=order_id, seller=seller)
        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if not order.can_transition_to(new_status):
            return Response(
                {"error": f"Cannot change status from '{order.status}' to '{new_status}'"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if new_status == "cancelled" and order.status != "cancelled":
            for item in order.items.select_related("product"):
                item.product.stock_quantity += item.quantity
                item.product.save()

        order.status = new_status
        if new_status == "delivered":
            order.delivered_at = timezone.now()
        order.save()

    return Response(OrderSerializer(order, context={"request": request}).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def order_confirm_delivery_view(request, order_id):
    customer, error = get_customer_or_error(request)
    if error:
        return error
    try:
        order = Order.objects.get(id=order_id, customer=customer)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status != "delivered":
        return Response({"error": "Order has not been marked as delivered yet"}, status=status.HTTP_400_BAD_REQUEST)
    if order.customer_confirmed_at is not None:
        return Response({"error": "Delivery already confirmed"}, status=status.HTTP_400_BAD_REQUEST)

    order.confirm_by_customer()
    return Response(OrderSerializer(order, context={"request": request}).data)


@api_view(["DELETE"])
@permission_classes([IsAuthenticated])
def order_delete_view(request, order_id):
    seller, error = get_seller_or_error(request)
    if error:
        return error
    try:
        order = Order.objects.get(id=order_id, seller=seller)
    except Order.DoesNotExist:
        return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

    if order.status != "cancelled":
        return Response(
            {"error": "Only cancelled orders can be removed from your list. Cancel the order first."},
            status=status.HTTP_400_BAD_REQUEST
        )

    order.hidden_from_seller = True
    order.save()
    return Response(status=status.HTTP_204_NO_CONTENT)
