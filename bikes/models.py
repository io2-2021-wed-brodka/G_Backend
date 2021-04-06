import uuid

from django.db import models


class BikeStatus:
    working = "working"
    in_service = "in_service"
    blocked = "blocked"

    CHOICES = ((working, "Working"), (in_service, "In service"), (blocked, "Blocked"))


class Bike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=20, choices=BikeStatus.CHOICES, default=BikeStatus.working
    )
    station = models.ForeignKey(
        "stations.Station", on_delete=models.SET_NULL, null=True, blank=True
    )
    user = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return f"Bike {self.id} ({self.status}), at station {self.station.name}"
