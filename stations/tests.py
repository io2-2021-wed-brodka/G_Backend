from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework import status

from stations.models import Station


class StationCreateTestCase(TestCase):
    def test_create_station_status_code(self):
        response = self.client.post(
            reverse("station-list"), {"name": "Good 'ol station"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_station_body(self):
        response = self.client.post(
            reverse("station-list"), {"name": "Good 'ol station"}
        )
        station = Station.objects.first()
        self.assertEqual(response.data, {"id": station.id, "name": station.name})


class StationGetTestCase(TestCase):
    def test_get_station_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_station_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(response.data, {"id": station.id, "name": station.name})


class StationsGetTestCase(TestCase):
    def test_get_stations_status_code(self):
        response = self.client.get(reverse("station-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_stations_body(self):
        station1 = Station.objects.create(name="Good 'ol station 1")
        station2 = Station.objects.create(name="Good 'ol station 2")
        response = self.client.get(reverse("station-list"))
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


class StationDeleteTestCase(TestCase):
    def test_delete_station_successful_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.delete(
            reverse("station-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_station_successful_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.delete(
            reverse("station-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(
            response.data,
            {
                "id": station.id,
                "name": station.name,
            },
        )

    def test_delete_station_successful_doesnt_exist(self):
        station = Station.objects.create(name="Good 'ol station")
        self.client.delete(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertFalse(Station.objects.filter(id=station.id).exists())
