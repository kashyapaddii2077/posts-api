import random
import string

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
            "tax_rate",
            "quantity",
            "gst",
            "image",
            "is_deleted",
            "created_at",
            "updated_at",
            "stock_status",
        ]

        read_only_fields = [
            "id",
            "sku",
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

    def create(self, validated_data):

        while True:
            letters = "".join(
                random.choices(string.ascii_uppercase, k=3)
            )

            numbers = "".join(
                random.choices(string.digits, k=6)
            )

            sku = f"PRD-{letters}{numbers}"

            if not Product.objects.filter(sku=sku).exists():
                break

        validated_data["sku"] = sku

        return Product.objects.create(**validated_data)

    stock_status = serializers.SerializerMethodField()

    def get_stock_status(self, obj):
        if obj.stock == 0:
            return "Out of Stock"

        if obj.stock <= 10:
            return "Low Stock"

        return "In Stock"
