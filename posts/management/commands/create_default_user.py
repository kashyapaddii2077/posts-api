from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Create the default API user"

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username="testuser",
            defaults={
                "is_active": True,
            },
        )

        if created:
            user.set_password("Test@12345")
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f"User created successfully. ID: {user.id}"
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(
                    f"User already exists. ID: {user.id}"
                )
            )
            