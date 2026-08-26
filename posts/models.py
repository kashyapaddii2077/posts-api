from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    related_name="posts",
    null=True,
    blank=True
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
    