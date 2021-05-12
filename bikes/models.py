import uuid

from django.db import models
from django.utils import timezone

from core.exceptions import BusinessLogicError
from stations.models import Station
from users.models import User


class BikeStatus(models.TextChoices):
    available = "available"
    rented = "rented"
    reserved = "reserved"
    blocked = "blocked"


class Bike(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.CharField(
        max_length=9, choices=BikeStatus.choices, default=BikeStatus.available
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

    def rent(self, user):
        # the fact we have to use hasattr is a shameful stain on Django's reputation
        # source: https://stackoverflow.com/a/40743258/8888856
        if hasattr(self, "reservation"):
            if self.reservation.user != user:
                raise BusinessLogicError(
                    "User renting the bike is not the one that reserved the bike"
                )
            self.reservation.delete()
        self.user = user
        self.status = BikeStatus.rented
        self.station = None
        self.save()

    def return_to_station(self, station: Station):
        self.station = station
        self.status = BikeStatus.available
        self.user = None
        self.save()

    def reserve(self, user: User):
        time = timezone.now()
        Reservation.objects.create(
            bike=self,
            user=user,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )
        self.status = BikeStatus.reserved
        self.save()

    def cancel_reservation(self):
        self.reservation.delete()
        self.status = BikeStatus.available
        self.save()

    def block(self):
        self.status = BikeStatus.blocked
        self.save()

    def unblock(self):
        self.status = BikeStatus.available
        self.save()


class Reservation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    bike = models.OneToOneField(
        "bikes.Bike",
        on_delete=models.CASCADE,
        related_name="reservation",
    )
    user = models.ForeignKey(
        "users.User",
        on_delete=models.CASCADE,
        related_name="reservations",
    )
    reserved_at = models.DateTimeField()
    reserved_till = models.DateTimeField()
