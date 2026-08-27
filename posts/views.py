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
from .pagination import PostPagination
from .serializers import PostSerializer
from .user_serializers import UserSerializer


class PostViewSet(ModelViewSet):

    serializer_class = PostSerializer
    permission_classes = [AllowAny]
    parser_classes = [MultiPartParser, FormParser]

    filter_backends = [SearchFilter]
    search_fields = ["title", "body"]

    pagination_class = PostPagination

    def get_permissions(self):
        if self.action in ["create", "bulk_create"]:
            return [IsAuthenticated()]

        return [AllowAny()]

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
                            "JSON array of posts. Example: "
                            '[{"title": "Post 1", "body": "Body 1"}, '
                            '{"title": "Post 2", "body": "Body 2"}]'
                        )
                    ),
                    "files": serializers.ListField(
                        child=serializers.FileField(),
                        help_text=(
                            "Upload one file for each post. "
                            "Files must be in the same order as posts."
                        ),
                    ),
                },
            ),
        ),
        responses=PostSerializer(many=True),
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="bulk-create",
    )
    def bulk_create(self, request, *args, **kwargs):

        # Get posts from multipart form data
        posts_data = request.data.get("posts")

        if not posts_data:
            return Response(
                {"error": "posts field is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Convert bytes to string if required
        if isinstance(posts_data, bytes):
            posts_data = posts_data.decode("utf-8")

        # Swagger sends the posts field as a JSON string
        if isinstance(posts_data, str):

            posts_data = posts_data.strip()

            # Swagger can send:
            # [{"title":"Post 1","body":"Body 1"}, ...]
            #
            # Parse that JSON string into a Python list.
            try:
                posts_data = json.loads(posts_data)

            except (json.JSONDecodeError, TypeError):
                return Response(
                    {
                        "error": "Invalid JSON in posts field.",
                        "received": posts_data,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        # At this point posts_data must be a list
        if not isinstance(posts_data, list):
            return Response(
                {
                    "error": "posts must be a JSON list.",
                    "received_type": type(posts_data).__name__,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not posts_data:
            return Response(
                {"error": "At least one post is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Get uploaded files
        files = request.FILES.getlist("files")

        # One file is required for every post
        if len(files) != len(posts_data):
            return Response(
                {
                    "error": (
                        f"The number of files ({len(files)}) "
                        f"must match the number of posts "
                        f"({len(posts_data)})."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializers_list = []

        # Validate every post before creating anything
        for post_data in posts_data:

            if not isinstance(post_data, dict):
                return Response(
                    {
                        "error": (
                            "Each item in posts must be "
                            "a JSON object."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(
                data=post_data
            )

            serializer.is_valid(
                raise_exception=True
            )

            serializers_list.append(serializer)

        created_posts = []

        # Create all posts as one transaction
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

        # Return all created posts
        response_serializer = self.get_serializer(
            created_posts,
            many=True,
        )

        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def get_queryset(self):

        queryset = Post.objects.all().order_by(
            "-created_at"
        )

        user_id = self.request.query_params.get(
            "user_id"
        )

        if user_id:
            queryset = queryset.filter(
                user_id=user_id
            )

        return queryset


class UserViewSet(ReadOnlyModelViewSet):

    queryset = User.objects.all().order_by("id")

    serializer_class = UserSerializer

    permission_classes = [AllowAny]