import csv

from django.http import HttpResponse
from rest_framework.decorators import action

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


@action(
    detail=False,
    methods=["get"],
    url_path="cards",
)
def cards(self, request):

    queryset = self.get_queryset().filter(
        is_deleted=False
    )

    total_products = queryset.count()

    in_stock = queryset.filter(
        stock__gt=10
    ).count()

    low_stock = queryset.filter(
        stock__gt=0,
        stock__lte=10
    ).count()

    out_of_stock = queryset.filter(
        stock=0
    ).count()

    return Response({
        "status": True,
        "data": {
            "total_products": total_products,
            "in_stock": in_stock,
            "out_of_stock": out_of_stock,
            "low_stock": low_stock,
        },
    })

    

    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export(self, request):

        queryset = self.filter_queryset(self.get_queryset())

        response = HttpResponse(
            content_type="text/csv"
        )

        response["Content-Disposition"] = (
            'attachment; filename="products.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "SKU",
            "Name",
            "Category",
            "Price",
            "Stock",
            "Quantity",
            "Stock Status",
            "Tax Rate",
            "GST",
        ])

        for product in queryset:
            stock_status = (
                "Out of Stock"
                if product.quantity == 0
                else "In Stock"
            )

            writer.writerow([
                product.sku,
                product.name,
                product.category,
                product.price,
                product.stock,
                product.quantity,
                stock_status,
                product.tax_rate,
                product.gst,
            ])

        return response




        

    def get_queryset(self):

        is_deleted = self.request.query_params.get("isDeleted")
        category = self.request.query_params.get("category")

        queryset = Product.objects.all()

        if is_deleted is None:
            pass

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
        {
            "status": 204,
            "message": "The item has been deleted",
        },
        status=status.HTTP_200_OK,
        )



