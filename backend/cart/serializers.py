from rest_framework import serializers

from .models import CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(source="product.id", read_only=True)
    name = serializers.CharField(source="product.name", read_only=True)
    price = serializers.DecimalField(source="product.price", max_digits=10, decimal_places=2, read_only=True)
    image_path = serializers.SerializerMethodField()
    stock_quantity = serializers.IntegerField(source="product.stock_quantity", read_only=True)
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)

    class Meta:
        model = CartItem
        fields = ["id", "product_id", "name", "price", "image_path", "stock_quantity", "seller_id", "quantity"]

    def get_image_path(self, obj):
        if not obj.product.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.product.image.url)
        return obj.product.image.url


class CartItemCreateSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)


class CartItemUpdateSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)
