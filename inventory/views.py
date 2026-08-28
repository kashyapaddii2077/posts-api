from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from .models import Inventory
from .serializers import InventorySerializer


class InventoryViewSet(ModelViewSet):

    queryset = Inventory.objects.filter(
        is_deleted=False
    ).order_by("-created_at")

    serializer_class = InventorySerializer

    filter_backends = [SearchFilter]

    search_fields = [
        "product__sku",
        "product__name",
        "product__category",
    ]

    def get_permissions(self):

        if self.action == "create":
            return [IsAuthenticated()]

        return [AllowAny()]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="isDeleted",
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
                required=False,
                description=(
                    "Filter inventory by deletion status. "
                    "true returns only deleted inventory, "
                    "false returns only active inventory."
                ),
            ),
        ]
    )
    def list(self, request, *args, **kwargs):

        is_deleted = request.query_params.get("isDeleted")

        if is_deleted is None:
            queryset = Inventory.objects.filter(
                is_deleted=False
            ).order_by("-created_at")

        elif is_deleted.lower() == "true":
            queryset = Inventory.objects.filter(
                is_deleted=True
            ).order_by("-created_at")

        elif is_deleted.lower() == "false":
            queryset = Inventory.objects.filter(
                is_deleted=False
            ).order_by("-created_at")

        else:
            return Response(
                {
                    "status": False,
                    "message": "isDeleted must be true or false."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(queryset)

        page = self.paginate_queryset(queryset)

        if page is not None:

            serializer = self.get_serializer(
                page,
                many=True,
            )

            return Response({
                "status": True,
                "data": serializer.data,
                "pagination": {
                    "page": int(
                        request.query_params.get(
                            "page",
                            1,
                        )
                    ),
                    "current": len(page),
                    "totalProduct": queryset.count(),
                },
            })

        serializer = self.get_serializer(
            queryset,
            many=True,
        )

        return Response({
            "status": True,
            "data": serializer.data,
            "pagination": {
                "page": 1,
                "current": len(serializer.data),
                "totalProduct": queryset.count(),
            },
        })

    def destroy(self, request, *args, **kwargs):

        inventory = self.get_object()

        inventory.is_deleted = True
        inventory.save(update_fields=["is_deleted"])

        return Response(
            {
                "status": True,
                "message": "Inventory deleted successfully."
            },
            status=status.HTTP_200_OK,
        )

