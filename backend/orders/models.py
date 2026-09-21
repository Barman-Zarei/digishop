from django.db import models
from django.utils import timezone

from accounts.models import Customer, Seller
from products.models import Product


class CheckoutSession(models.Model):
    """Holds cart snapshot + shipping info while payment is in progress.
    Nothing here touches stock or creates real Orders until payment is verified."""

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("expired", "Expired"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="checkout_sessions")
    shipping_address = models.TextField()
    shipping_phone = models.CharField(max_length=20)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    cart_snapshot = models.JSONField()  # [{product_id, quantity, price, seller_id}, ...]
    zarinpal_authority = models.CharField(max_length=64, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CheckoutSession #{self.id} ({self.status})"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("paid", "Paid"),
        ("refund_due", "Refund Due"),
        ("refunded", "Refunded"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    shipping_address = models.TextField(default="")
    shipping_phone = models.CharField(max_length=20, default="")

    payment_status = models.CharField(max_length=12, choices=PAYMENT_STATUS_CHOICES, default="paid")
    zarinpal_ref_id = models.CharField(max_length=64, blank=True, null=True)

    delivered_at = models.DateTimeField(blank=True, null=True)
    customer_confirmed_at = models.DateTimeField(blank=True, null=True)

    order_date = models.DateTimeField(auto_now_add=True)

    def mark_delivered(self):
        self.status = "delivered"
        self.delivered_at = timezone.now()
        self.save()

    def confirm_by_customer(self):
        self.customer_confirmed_at = timezone.now()
        self.save()

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} x{self.quantity}"
