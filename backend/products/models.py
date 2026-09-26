from django.core.exceptions import ValidationError
from django.db import models
from PIL import Image

from accounts.models import Seller

MAX_IMAGE_DIMENSION = 3000
MAX_IMAGE_SIZE_MB = 5


def validate_product_image(image_file):
    if image_file.size > MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise ValidationError(f"Image must be under {MAX_IMAGE_SIZE_MB}MB")
    try:
        image_file.seek(0)
        with Image.open(image_file) as img:
            width, height = img.size
    except Exception:
        raise ValidationError("Uploaded file is not a valid image")
    finally:
        image_file.seek(0)
    if width > MAX_IMAGE_DIMENSION or height > MAX_IMAGE_DIMENSION:
        raise ValidationError(f"Image dimensions must be at most {MAX_IMAGE_DIMENSION}x{MAX_IMAGE_DIMENSION}px")


class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name="products")
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=14, decimal_places=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
