import uuid

from django.db import models


class StationState:
    working = 0
    blocked = 1

    CHOICES = (
        (working, "Working"),
        (blocked, "Blocked"),
    )


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    state = models.PositiveSmallIntegerField(
        choices=StationState.CHOICES, default=StationState.working
    )
    name = models.CharField(max_length=255)

    def __str__(self):
        return f"Station at {self.name} ({self.state})"

    def block(self):
        self.state = StationState.blocked
        self.save()
