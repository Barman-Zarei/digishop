from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    image_path = serializers.CharField(source="product.image_path", read_only=True)
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "name", "price", "image_path", "seller_id", "quantity"]


class CartItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
