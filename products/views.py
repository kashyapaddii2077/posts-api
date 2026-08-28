from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Product
from .serializers import ProductSerializer


class ProductViewSet(ModelViewSet):

    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]

    search_fields = [
        "sku",
        "name",
        "category",
    ]

    def get_queryset(self):
        return Product.objects.filter(
            is_deleted=False
        ).order_by("-created_at")

    def get_permissions(self):

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsAuthenticated()]

        return [AllowAny()]

    def destroy(self, request, *args, **kwargs):

        product = self.get_object()

        product.is_deleted = True
        product.save(
            update_fields=[
                "is_deleted",
                "updated_at",
            ]
        )

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )
