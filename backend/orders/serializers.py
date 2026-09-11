from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = OrderItem
        fields = ["id", "product_id", "name", "image_path", "quantity", "unit_price"]

    def get_image_path(self, obj):
        if not obj.product.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.product.image.url)
        return obj.product.image.url


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    store_name = serializers.CharField(source="seller.store_name", read_only=True)
    customer_name = serializers.CharField(source="customer.full_name", read_only=True)

    class Meta:
        model = Order
        fields = ["id", "store_name", "customer_name", "order_date", "total_amount", "status", "items"]


class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)
