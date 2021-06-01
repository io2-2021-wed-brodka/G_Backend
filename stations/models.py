import uuid

from django.db import models


class StationStatus(models.TextChoices):
    working = "active"
    blocked = "blocked"


class Station(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=7,
        choices=StationStatus.choices,
        default=StationStatus.working,
        editable=False,
    )
    name = models.CharField(max_length=255)
    bikesLimit = models.PositiveIntegerField(default=10)

    def __str__(self):
        return f"Station at {self.name} ({self.status})"

    def block(self):
        self.status = StationStatus.blocked
        self.save()

    def unblock(self):
        self.status = StationStatus.working
        self.save()

    def cancel_all_reservations(self):
        from bikes.models import BikeStatus

        bikes = self.bikes.all()
        # TODO(arkadiusz-gorecki): optimize this to fix N + 1 problem
        for bike in bikes:
            if bike.status == BikeStatus.reserved:
                bike.cancel_reservation()
