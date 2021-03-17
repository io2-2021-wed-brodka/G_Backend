from django.db import models


class BikeState:
    working = "working"
    in_service = "in_service"
    blocked = "blocked"

    CHOICES = (
        (working, "Working"),
        (in_service, "In service"),
        (blocked, "Blocked"),
    )


class Bike(models.Model):
    state = models.CharField(max_length=20, choices=BikeState.CHOICES, default=BikeState.working)
    station = models.ForeignKey("stations.Station", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Bike {self.id} ({self.state}), at station {self.station.location}"
