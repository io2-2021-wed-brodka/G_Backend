from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework import status

from bikes.models import Bike, BikeStatus
from stations.models import Station, StationState
from users.models import User


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
        self.assertEqual(response.data, {"id": str(station.id), "name": station.name})


class StationGetTestCase(TestCase):
    def test_get_station_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_station_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(response.data, {"id": str(station.id), "name": station.name})


class StationsGetTestCase(TestCase):
    def test_get_stations_status_code(self):
        response = self.client.get(reverse("station-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_stations_body(self):
        station1 = Station.objects.create(name="Good 'ol station 1")
        station2 = Station.objects.create(name="Good 'ol station 2")
        # make sure blocked stations are not listed
        Station.objects.create(name="Good 'ol station 1", state=StationState.blocked)
        response = self.client.get(reverse("station-list"))
        self.assertEqual(
            response.data,
            [
                {
                    "id": str(station1.id),
                    "name": station1.name,
                },
                {
                    "id": str(station2.id),
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
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_station_successful_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.delete(
            reverse("station-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.data, None)

    def test_delete_station_successful_doesnt_exist(self):
        station = Station.objects.create(name="Good 'ol station")
        self.client.delete(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertFalse(Station.objects.filter(id=station.id).exists())

    def test_delete_station_has_bikes_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        Bike.objects.create(station=station)
        response = self.client.delete(
            reverse("station-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_delete_station_has_bikes_body(self):
        station = Station.objects.create(name="Good 'ol station")
        Bike.objects.create(station=station)
        response = self.client.delete(
            reverse("station-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.data, {"message": "station has bikes"})

    def test_delete_station_not_found_status_code(self):
        response = self.client.delete(reverse("station-detail", kwargs={"pk": "abc"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_station_not_found_body(self):
        response = self.client.delete(reverse("station-detail", kwargs={"pk": "abc"}))
        self.assertEqual(response.data, {"message": "station not found"})


class StationBlockTestCase(TestCase):
    def test_block_station_successful_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.post(reverse("station-blocked"), {"id": f"{station.id}"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_block_station_successful_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.post(reverse("station-blocked"), {"id": f"{station.id}"})
        self.assertEqual(response.data, {"id": str(station.id), "name": station.name})

    def test_delete_station_not_found(self):
        station = Station.objects.create(name="Good 'ol station")
        delete_id = station.id
        Station.objects.filter(id=station.id).delete()
        response = self.client.post(reverse("station-blocked"), {"id": f"{delete_id}"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_station_already_blocked(self):
        station = Station.objects.create(
            name="Good 'ol station", state=StationState.blocked
        )
        response = self.client.post(reverse("station-blocked"), {"id": f"{station.id}"})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class StationReturnBikeTestCase(TestCase):
    def test_return_bike_successful_status_code(self):
        user = User.objects.create(first_name="John6", last_name="Doe")
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=user, station=None, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_return_bike_successful_body(self):
        user = User.objects.create(first_name="John6", last_name="Doe")
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=user, station=None, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(
            response.data,
            {
                "id": str(returned_bike.id),
                "station": {
                    "id": str(station.id),
                    "name": station.name,
                },
                "user": None,
                "status": BikeStatus.available,
            },
        )

    def test_return_bike_not_found(self):
        user = User.objects.create(first_name="John6", last_name="Doe")
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=user, station=None, status=BikeStatus.rented
        )
        delete_id = returned_bike.id
        Bike.objects.filter(id=returned_bike.id).delete()
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}), {"id": f"{delete_id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_bike_station_not_none(self):
        user = User.objects.create(first_name="John6", last_name="Doe")
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_return_bike_station_blocked(self):
        user = User.objects.create(first_name="John6", last_name="Doe")
        station = Station.objects.create(
            name="Station Name", state=StationState.blocked
        )
        returned_bike = Bike.objects.create(
            user=user, station=None, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
