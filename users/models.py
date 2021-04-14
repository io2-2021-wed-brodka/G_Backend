import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole:
    user = "user"
    tech = "tech"
    admin = "admin"

    CHOICES = (
        (user, "User"),
        (tech, "Tech"),
        (admin, "Admin"),
    )


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(max_length=32, choices=UserRole.CHOICES)

    def __str__(self):
        return f"{self.name} ({self.role})"

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"
