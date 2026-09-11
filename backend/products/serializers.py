from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    seller_id = serializers.IntegerField(source="seller.id", read_only=True)
    store_name = serializers.CharField(source="seller.store_name", read_only=True)
    image_path = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            "id", "seller_id", "store_name", "name", "description",
            "price", "stock_quantity", "image_path", "created_at"
        ]

    def get_image_path(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url


class ProductCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock_quantity", "image"]

    def create(self, validated_data):
        seller = self.context["request"].user.seller
        return Product.objects.create(seller=seller, **validated_data)


class ProductUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["name", "description", "price", "stock_quantity", "image"]
        extra_kwargs = {
            "name": {"required": False},
            "price": {"required": False},
            "stock_quantity": {"required": False},
        }
