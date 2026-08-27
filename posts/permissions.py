from rest_framework.permissions import BasePermission


class IsOwnerOrAdmin(BasePermission):
    """
    Admin users can modify any post.
    Normal users can modify only their own posts.
    """

    def has_object_permission(self, request, view, obj):

        if request.user.is_staff:
            return True

        return obj.user == request.user