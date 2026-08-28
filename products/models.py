from django.db import models


class Product(models.Model):

    TAX_RATE_CHOICES = [
        (5, "5%"),
        (10, "10%"),
        (15, "15%"),
        (20, "20%"),
    ]

    sku = models.CharField(
        max_length=100,
        unique=True,
    )

    name = models.CharField(
        max_length=255,
    )

    image = models.ImageField(
        upload_to="products/",
        blank=True,
        null=True,
    )

    category = models.CharField(
        max_length=100,
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    stock = models.PositiveIntegerField(
        default=0,
    )

    quantity = models.PositiveIntegerField(
        default=0,
    )

    tax_rate = models.PositiveIntegerField(
        choices=TAX_RATE_CHOICES,
    )

    gst = models.PositiveIntegerField(
        default=0,
    )

    is_deleted = models.BooleanField(
        default=False,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return self.name