from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="product.name", read_only=True)

    class Meta:
        model = OrderItem
        fields = ["id", "name", "quantity", "unit_price"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    customer_name = serializers.CharField(source="customer.user.username", read_only=True)
    store_name = serializers.CharField(source="seller.store_name", read_only=True)
    seller_phone = serializers.CharField(source="seller.phone", read_only=True)
    seller_bank_account = serializers.CharField(source="seller.bank_account_number", read_only=True)
    can_confirm_delivery = serializers.SerializerMethodField()
    fraud_report_available = serializers.BooleanField(read_only=True)
    seller_national_id = serializers.SerializerMethodField()
    seller_legal_name = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = [
            "id", "customer_name", "store_name", "seller_phone", "seller_bank_account",
            "total_amount", "status", "shipping_address", "shipping_phone",
            "delivered_at", "customer_confirmed_at", "order_date", "items",
            "can_confirm_delivery", "fraud_report_available",
            "seller_national_id", "seller_legal_name",
        ]

    def get_can_confirm_delivery(self, obj):
        return obj.customer_confirmed_at is None

    def get_seller_national_id(self, obj):
        return obj.seller.national_id if obj.fraud_report_available else None

    def get_seller_legal_name(self, obj):
        return obj.seller.legal_full_name if obj.fraud_report_available else None


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
