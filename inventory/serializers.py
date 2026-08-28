from rest_framework import serializers

from .models import Inventory


class InventorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Inventory

        fields = [
            "id",
            "product",
            "quantity",
            "created_at",
            "updated_at",
        ]

        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
        ]

