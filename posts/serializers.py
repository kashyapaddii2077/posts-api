from rest_framework import serializers

from .models import Post


class PostSerializer(serializers.ModelSerializer):

    file = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = Post

        fields = [
            "id",
            "user",
            "title",
            "body",
            "file",
            "created_at",
            "updated_at",
            "role",
        ]

        read_only_fields = [
            "id",
            "user",
            "created_at",
            "updated_at",
            "role",
        ]

    def get_file(self, obj):

        if not obj.file:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(
                obj.file.url
            )

        return obj.file.url

    def get_role(self, obj):

        if not obj.user:
            return None

        return "Admin" if obj.user.is_staff else "User"
