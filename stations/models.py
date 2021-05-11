import uuid

from django.db import models


class StationState(models.TextChoices):
    working = "working"
    blocked = "blocked"


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(
        max_length=7,
        choices=StationState.choices,
        default=StationState.working,
        editable=False,
    )
    name = models.CharField(max_length=255)
    capacity = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"Station at {self.name} ({self.state})"

    def block(self):
        self.state = StationState.blocked
        self.save()

    def unblock(self):
        self.state = StationState.working
        self.save()
