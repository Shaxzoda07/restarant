import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "ADMIN_USERNAME / ADMIN_PASSWORD muhit o'zgaruvchilaridan admin yaratadi"

    def handle(self, *args, **options):
        username = os.environ.get("ADMIN_USERNAME")
        password = os.environ.get("ADMIN_PASSWORD")
        if not username or not password:
            self.stdout.write("ADMIN_USERNAME/ADMIN_PASSWORD berilmagan — o'tkazib yuborildi")
            return
        User = get_user_model()
        user, created = User.objects.get_or_create(username=username, defaults={"is_staff": True, "is_superuser": True})
        if created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f"Admin yaratildi: {username}"))
        else:
            self.stdout.write("Admin allaqachon mavjud")
