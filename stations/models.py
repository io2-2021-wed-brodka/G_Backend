import uuid

from django.db import models


class StationState:
    working = "working"
    blocked = "blocked"

    CHOICES = (
        (working, "Working"),
        (blocked, "Blocked"),
    )


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.CharField(
        max_length=20, choices=StationState.CHOICES, default=StationState.working
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Station at {self.name} ({self.state})"
