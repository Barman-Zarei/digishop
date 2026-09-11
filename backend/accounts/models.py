from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="customer")
    full_name = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.full_name


class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="seller")
    store_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.store_name
