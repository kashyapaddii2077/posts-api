from django.db import models


class Customer(models.Model):

    CUSTOMER_TYPE_CHOICES = [
        ("Individual", "Individual"),
        ("Business", "Business"),
    ]

    STATUS_CHOICES = [
        ("Active", "Active"),
        ("Inactive", "Inactive"),
        ("Blocked", "Blocked"),
    ]

    name = models.CharField(
        max_length=255,
    )

    company = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    email = models.EmailField()

    phone = models.CharField(
        max_length=20,
    )

    customer_type = models.CharField(
        max_length=20,
        choices=CUSTOMER_TYPE_CHOICES,
    )

    profile_image = models.ImageField(
        upload_to="customers/",
        blank=True,
        null=True,
    )

    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    outstanding_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0.00,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Active",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    is_deleted = models.BooleanField(
        default=False,
    )

    def __str__(self):
        return self.name