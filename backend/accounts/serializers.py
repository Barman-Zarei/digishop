from django.db import transaction
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from .models import User, Customer, Seller

import re

NATIONAL_ID_RE = re.compile(r"^[0-9]{10}$")
CARD_NUMBER_RE = re.compile(r"^[0-9]{16}$")
IBAN_RE = re.compile(r"^IR[0-9]{24}$")


class RegisterSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=100)
    address = serializers.CharField(required=False, allow_blank=True)

    def validate_username(self, value):
        if User.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Username already taken")
        return value

    def validate_password(self, value):
        validate_password(value)
        return value

    def create(self, validated_data):
        with transaction.atomic():
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
        if not NATIONAL_ID_RE.fullmatch(value):
            raise serializers.ValidationError("National ID must be exactly 10 ASCII digits (0-9)")
        return value

    def validate_bank_account_number(self, value):
        cleaned = value.replace(" ", "").replace("-", "").upper()
        if cleaned.startswith("IR"):
            if not IBAN_RE.fullmatch(cleaned):
                raise serializers.ValidationError("Enter a valid IBAN: IR followed by 24 digits")
        elif not CARD_NUMBER_RE.fullmatch(cleaned):
            raise serializers.ValidationError("Enter a valid 16-digit card number or an IBAN starting with IR")
        return cleaned

    def validate(self, attrs):
        request = self.context["request"]
        if Seller.objects.filter(user=request.user).exists():
            raise serializers.ValidationError("You are already a seller")
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        return Seller.objects.create(user=request.user, **validated_data)
