import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    user = "user"
    tech = "tech"
    admin = "admin"


class UserState(models.TextChoices):
    active = "active"
    blocked = "blocked"


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    role = models.CharField(
        max_length=5, choices=UserRole.choices, default=UserRole.user
    )
    state = models.CharField(
        max_length=7, choices=UserState.choices, default=UserState.active
    )
    rental_limit = models.PositiveSmallIntegerField(default=4)

    def __str__(self):
        return f"{self.name} ({self.role}, {self.state})"

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def block(self):
        self.state = UserState.blocked
        self.save()

    def unblock(self):
        self.state = UserState.active
        self.save()
