import json

from django.contrib.auth.models import User
from django.db import transaction

from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from drf_spectacular.utils import (
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    inline_serializer,
    OpenApiRequest,
)

from .models import Post
from .serializers import PostSerializer
from .user_serializers import UserSerializer
from .pagination import PostPagination


class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ["create", "bulk_create"]:
            return [IsAuthenticated()]
        return [AllowAny()]

    filter_backends = [SearchFilter]
    search_fields = ["title", "body"]

    pagination_class = PostPagination

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Search posts by title or body.",
            ),
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter posts by user ID.",
            ),
            OpenApiParameter(
                name="page",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Page number.",
            ),
            OpenApiParameter(
                name="page_size",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Number of posts per page.",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @extend_schema(
        request=OpenApiRequest(
            request=inline_serializer(
                name="BulkCreatePostRequest",
                fields={
                    "posts": serializers.CharField(
                        help_text=(
                            'JSON array of posts. Example: '
                            '[{"title": "Post 1", "body": "Body 1"}, '
                            '{"title": "Post 2", "body": "Body 2"}]'
                        )
                    ),
                    "files": serializers.ListField(
                        child=serializers.FileField(),
                        help_text=(
                            "Upload one file for each post. "
                            "Files must be in the same order as posts."
                        )
                    ),
                },
            ),
            encoding={
                "posts": {
                    "contentType": "application/json"
                },
                "files": {
                    "contentType": "application/octet-stream"
                },
            },
        ),
        responses=PostSerializer(many=True),
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-create",
    )
    def bulk_create(self, request, *args, **kwargs):

        posts_data = request.data.get("posts")

        if not posts_data:
            return Response(
                {"error": "posts field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )


        if isinstance(posts_data, str):
            try:
                    posts_data = json.loads(posts_data)
            except json.JSONDecodeError:
                return Response(
                {"error": "posts must contain valid JSON."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Handle JSON object containing a "posts" list
        if isinstance(posts_data, dict) and "posts" in posts_data:
            posts_data = posts_data["posts"]

        if not isinstance(posts_data, list):
            return Response(
                {"error": "posts must be a JSON list."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        

        if not posts_data:
            return Response(
                {"error": "At least one post is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        files = request.FILES.getlist("files")

        if len(files) != len(posts_data):
            return Response(
                {
                    "error": (
                        "The number of files must match "
                        "the number of posts."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializers_list = []

        for post_data in posts_data:

            serializer = self.get_serializer(
                data=post_data
            )

            serializer.is_valid(
                raise_exception=True
            )

            serializers_list.append(serializer)

        created_posts = []

        with transaction.atomic():

            for serializer, uploaded_file in zip(
                serializers_list,
                files,
            ):
                post = serializer.save(
                    user=request.user,
                    file=uploaded_file,
                )

                created_posts.append(post)

        response_serializer = self.get_serializer(
            created_posts,
            many=True,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_queryset(self):
        queryset = Post.objects.all().order_by("-created_at")

        user_id = self.request.query_params.get("user_id")

        if user_id:
            queryset = queryset.filter(
                user_id=user_id
            )

        return queryset


class UserViewSet(ReadOnlyModelViewSet):

    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializer
    permission_classes = [AllowAny]