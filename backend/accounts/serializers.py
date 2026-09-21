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
    store_name = serializers.CharField(min_length=2, max_length=150)
    phone = serializers.CharField(min_length=8, max_length=20)
    national_id = serializers.CharField(min_length=10, max_length=10)
    legal_full_name = serializers.CharField(min_length=3, max_length=150)
    bank_account_number = serializers.CharField(min_length=10, max_length=34)

    def validate_national_id(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("The National ID must consist only of numbers")
        return value

    def validate(self, attrs):
        request = self.context["request"]
        if Seller.objects.filter(user=request.user).exists():
            raise serializers.ValidationError("شما قبلاً فروشنده شده‌اید")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return Seller.objects.create(
            user=request.user,
            store_name=validated_data["store_name"],
            phone=validated_data["phone"],
            national_id=validated_data["national_id"],
            legal_full_name=validated_data["legal_full_name"],
            bank_account_number=validated_data["bank_account_number"],
        )
