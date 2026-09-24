from django.db import models
from django.utils import timezone

from accounts.models import Customer, Seller
from products.models import Product

FRAUD_REPORT_DELAY_DAYS = 3

VALID_TRANSITIONS = {
    "pending": {"confirmed", "cancelled"},
    "confirmed": {"shipped", "cancelled"},
    "shipped": {"delivered", "cancelled"},
    "delivered": set(),
    "cancelled": set(),
}


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name="orders")
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="orders")
    total_amount = models.DecimalField(max_digits=14, decimal_places=0)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")

    shipping_address = models.TextField(default="")
    shipping_phone = models.CharField(max_length=20, default="")

    delivered_at = models.DateTimeField(blank=True, null=True)
    customer_confirmed_at = models.DateTimeField(blank=True, null=True)

    order_date = models.DateTimeField(auto_now_add=True)

    def can_transition_to(self, new_status):
        return new_status in VALID_TRANSITIONS.get(self.status, set())

    def confirm_by_customer(self):
        self.customer_confirmed_at = timezone.now()
        self.save()

    @property
    def fraud_report_available(self):
        if self.delivered_at is None or self.customer_confirmed_at is not None:
            return False
        deadline = self.delivered_at + timezone.timedelta(days=FRAUD_REPORT_DELAY_DAYS)
        return timezone.now() >= deadline

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.RESTRICT)
    product_name = models.CharField(max_length=150)  # snapshot at time of purchase
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=0)

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"
