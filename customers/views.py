import csv

from django.http import HttpResponse
from django.utils import timezone

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .models import Customer
from .serializers import CustomerSerializer


class CustomerViewSet(ModelViewSet):

    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer

    filter_backends = [
        SearchFilter,
        OrderingFilter,
    ]

    search_fields = [
        "name",
        "company",
        "email",
        "phone",
    ]

    ordering_fields = [
        "name",
        "total_revenue",
        "outstanding_balance",
        "created_at",
        "updated_at",
    ]

    parser_classes = [
        MultiPartParser,
        FormParser,
    ]

    def get_queryset(self):

        queryset = Customer.objects.filter(
            is_deleted=False
        )

        customer_type = self.request.query_params.get(
            "customer_type"
        )

        customer_status = self.request.query_params.get(
            "status"
        )

        if customer_type:
            queryset = queryset.filter(
                customer_type=customer_type
            )

        if customer_status:
            queryset = queryset.filter(
                status=customer_status
            )

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
                            1
                        )
                    ),
                    "current": len(page),
                    "totalCustomer": queryset.count(),
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
                "totalCustomer": queryset.count(),
            },
        })

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(
            data=request.data
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_create(serializer)

        return Response(
            {
                "status": True,
                "message": "Customer created successfully.",
                "data": serializer.data,
            },
            status=status.HTTP_201_CREATED,
        )

    def retrieve(self, request, *args, **kwargs):

        customer = self.get_object()

        serializer = self.get_serializer(
            customer
        )

        return Response({
            "status": True,
            "data": serializer.data,
        })

    def update(self, request, *args, **kwargs):

        partial = kwargs.pop(
            "partial",
            False,
        )

        customer = self.get_object()

        serializer = self.get_serializer(
            customer,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(
            raise_exception=True
        )

        self.perform_update(serializer)

        return Response({
            "status": True,
            "message": "Customer updated successfully.",
            "data": serializer.data,
        })

    def destroy(self, request, *args, **kwargs):

        customer = self.get_object()

        customer.is_deleted = True

        customer.save(
            update_fields=[
                "is_deleted",
                "updated_at",
            ]
        )

        return Response(
            {
                "status": 200,
                "message": "The customer has been deleted.",
            },
            status=status.HTTP_200_OK,
        )

    @action(
        detail=False,
        methods=["get"],
        url_path="statistics",
    )
    def statistics(self, request):

        queryset = Customer.objects.filter(
            is_deleted=False
        )

        now = timezone.now()

        new_customers = queryset.filter(
            created_at__year=now.year,
            created_at__month=now.month,
        ).count()

        total_outstanding = sum(
            customer.outstanding_balance
            for customer in queryset
        )

        return Response({
            "status": True,
            "data": {
                "total_customers": queryset.count(),
                "active_customers": queryset.filter(
                    status="Active"
                ).count(),
                "new_customers": new_customers,
                "total_outstanding_balance": total_outstanding,
            },
        })

    @action(
        detail=False,
        methods=["get"],
        url_path="export",
    )
    def export(self, request):

        queryset = self.filter_queryset(
            self.get_queryset()
        )

        response = HttpResponse(
            content_type="text/csv"
        )

        response["Content-Disposition"] = (
            'attachment; filename="customers.csv"'
        )

        writer = csv.writer(response)

        writer.writerow([
            "ID",
            "Name",
            "Company",
            "Email",
            "Phone",
            "Customer Type",
            "Total Revenue",
            "Outstanding Balance",
            "Status",
            "Created At",
            "Updated At",
        ])

        for customer in queryset:

            writer.writerow([
                customer.id,
                customer.name,
                customer.company or "",
                customer.email,
                customer.phone,
                customer.customer_type,
                customer.total_revenue,
                customer.outstanding_balance,
                customer.status,
                customer.created_at,
                customer.updated_at,
            ])

        return response

