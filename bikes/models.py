import uuid

from django.db import models


class BikeStatus:
    available = 0
    rented = 1
    reserved = 2
    blocked = 3
    CHOICES = (
        (available, "Available"),
        (rented, "Rented"),
        (reserved, "Reserved"),
        (blocked, "Blocked"),
    )


class Bike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.PositiveSmallIntegerField(
        choices=BikeStatus.CHOICES, default=BikeStatus.available
    )
    station = models.ForeignKey(
        "stations.Station",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="bikes",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bikes",
    )

    def __str__(self):
        return f"Bike {self.id} ({self.status}), at station {self.station.name}"
