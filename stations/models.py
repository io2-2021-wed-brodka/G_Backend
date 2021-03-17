from django.db import models


class StationState:
    working = "working"
    blocked = "blocked"

    CHOICES = (
        (working, "Working"),
        (blocked, "Blocked"),
    )


class Station(models.Model):
    state = models.CharField(max_length=20, choices=StationState.CHOICES, default=StationState.working)
    location = models.CharField(max_length=255)

    def __str__(self):
        return f"Station at {self.location} ({self.state})"
