from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework import status

from bikes.models import Bike
from stations.models import Station
from users.models import User


class BikesCrudTestCase(TestCase):
    def test_create_bike(self):
        station = Station.objects.create(name="Station Name")
        response = self.client.post(reverse("bike-list"), {"stationId": station.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {"stationId": station.id})

    def test_get_bikes(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name")
        bike1 = Bike.objects.create(user=user, station=station)
        bike2 = Bike.objects.create(user=user, station=station)
        response = self.client.get(reverse("bike-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "id": bike1.id,
                    "station": {"id": bike1.station.id, "name": bike1.station.name},
                    "user": {"id": user.id, "name": user.name},
                    "status": bike1.status,
                },
                {
                    "id": bike2.id,
                    "station": {"id": bike2.station.id, "name": bike2.station.name},
                    "user": {"id": user.id, "name": user.name},
                    "status": bike2.status,
                },
            ],
        )
