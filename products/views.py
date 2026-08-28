from rest_framework.parsers import MultiPartParser, FormParser
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
    parser_classes = [MultiPartParser, FormParser]

    search_fields = [
        "sku",
        "name",
        "category",
    ]

    def get_queryset(self):

        is_deleted = self.request.query_params.get("isDeleted")
        category = self.request.query_params.get("category")

        queryset = Product.objects.all()

        if is_deleted is None:
            queryset = queryset.filter(is_deleted=False)

        elif is_deleted.lower() == "true":
            queryset = queryset.filter(is_deleted=True)

        elif is_deleted.lower() == "false":
            queryset = queryset.filter(is_deleted=False)

        else:
            return Product.objects.none()

        if category:
            queryset = queryset.filter(category__iexact=category)

        return queryset.order_by("-created_at")
    

    def get_permissions(self):

        if self.action in [
            "create",
            "update",
            "partial_update",
            "destroy",
        ]:
            return [IsAuthenticated()]

        return [AllowAny()]

    def list(self, request, *args, **kwargs):

        is_deleted = request.query_params.get("isDeleted")

        if (
            is_deleted is not None
            and is_deleted.lower() not in ["true", "false"]
        ):
            return Response(
                {
                    "status": False,
                    "message": "isDeleted must be true or false."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        queryset = self.filter_queryset(self.get_queryset())

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
                        request.query_params.get("page", 1)
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