from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Inventory
from .serializers import InventorySerializer


class InventoryViewSet(ModelViewSet):

    queryset = Inventory.objects.all().order_by("-created_at")
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

    def list(self, request, *args, **kwargs):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

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

    def update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Inventory update is not allowed."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Inventory update is not allowed."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def destroy(self, request, *args, **kwargs):

        return Response(
            {
                "detail": "Inventory delete is not allowed."
            },
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )