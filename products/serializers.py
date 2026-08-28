from rest_framework import serializers

from .models import Product


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product

        fields = [
            "id",
            "sku",
            "name",
            "category",
            "price",
            "stock",
            "quantity",
            "tax_rate",
            "gst",
            "is_deleted",
            "created_at",
            "updated_at",
            "image",
        ]

        read_only_fields = [
            "id",
            "is_deleted",
            "created_at",
            "updated_at",
        ]

    def validate_tax_rate(self, value):
        allowed_rates = [5, 10, 15, 20]

        if value not in allowed_rates:
            raise serializers.ValidationError(
                "Tax rate must be one of: 5, 10, 15, or 20."
            )

        return value