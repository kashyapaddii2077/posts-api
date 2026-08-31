from rest_framework import serializers

from .models import Customer


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer

        fields = [
            "id",
            "name",
            "company",
            "email",
            "phone",
            "customer_type",
            "profile_image",
            "total_revenue",
            "outstanding_balance",
            "status",
            "created_at",
            "updated_at",
            "is_deleted",
        ]

        read_only_fields = [
            "id",
            "total_revenue",
            "outstanding_balance",
            "created_at",
            "updated_at",
            "is_deleted",
        ]

    def validate_customer_type(self, value):
        allowed_types = ["Individual", "Business"]

        if value not in allowed_types:
            raise serializers.ValidationError(
                "Customer type must be Individual or Business."
            )

        return value

    def validate_status(self, value):
        allowed_statuses = [
            "Active",
            "Inactive",
            "Blocked",
        ]

        if value not in allowed_statuses:
            raise serializers.ValidationError(
                "Status must be Active, Inactive, or Blocked."
            )

        return value