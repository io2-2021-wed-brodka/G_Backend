from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework import status

from stations.models import Station


class StationCrudTestCase(TestCase):
    def test_create_station(self):
        response = self.client.post(
            reverse("station-list"), {"name": "Good 'ol station"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        station = Station.objects.first()
        self.assertEqual(response.data, {"id": station.id, "name": station.name})

    def test_get_station(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {"id": station.id, "name": station.name})

    def test_get_stations(self):
        station1 = Station.objects.create(name="Good 'ol station 1")
        station2 = Station.objects.create(name="Good 'ol station 2")
        response = self.client.get(reverse("station-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            [
                {
                    "id": station1.id,
                    "name": station1.name,
                },
                {
                    "id": station2.id,
                    "name": station2.name,
                },
            ],
        )

    def test_delete_station(self):
        pass
