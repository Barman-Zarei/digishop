from rest_framework import serializers

from .models import User, Customer, Seller


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=100)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            password=validated_data["password"],
            email=validated_data.get("email", ""),
            phone=validated_data.get("phone", "")
        )

        customer = Customer.objects.create(
            user=user,
            full_name=validated_data["full_name"],
            address=validated_data.get("address", ""),
            phone=validated_data.get("phone", "")
        )

        return customer


class CustomerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Customer
        fields = ["id", "username", "full_name", "address", "phone"]


class SellerSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Seller
        fields = ["id", "username", "store_name", "phone"]


class BecomeSellerSerializer(serializers.Serializer):
    store_name = serializers.CharField(max_length=100)
    phone = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        user = self.context["request"].user

        if Seller.objects.filter(user=user).exists():
            raise serializers.ValidationError("This user is already a seller")

        seller = Seller.objects.create(
            user=user,
            store_name=validated_data["store_name"],
            phone=validated_data.get("phone", "")
        )
        return seller
