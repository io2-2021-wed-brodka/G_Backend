from django.test import TestCase

from rest_framework.reverse import reverse
from rest_framework import status

from bikes.models import Bike, BikeStatus
from stations.models import Station, StationState
from users.models import User


class BikesGetTestCase(TestCase):
    def test_get_bikes_status_code(self):
        response = self.client.get(reverse("bike-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bikes_body(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name")
        bike1 = Bike.objects.create(user=user, station=station)
        bike2 = Bike.objects.create(user=user, station=station)
        response = self.client.get(reverse("bike-list"))
        self.assertEqual(
            response.data,
            [
                {
                    "id": str(bike1.id),
                    "station": {
                        "id": str(bike1.station.id),
                        "name": bike1.station.name,
                    },
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike1.status,
                },
                {
                    "id": str(bike2.id),
                    "station": {
                        "id": str(bike2.station.id),
                        "name": bike2.station.name,
                    },
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike2.status,
                },
            ],
        )


class BikeCreateTestCase(TestCase):
    def test_create_bike_status_code(self):
        station = Station.objects.create(name="Station Name")
        response = self.client.post(reverse("bike-list"), {"stationId": station.id})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_bike_body(self):
        station = Station.objects.create(name="Station Name")
        response = self.client.post(reverse("bike-list"), {"stationId": station.id})
        bike = Bike.objects.get(id=response.data["id"])
        self.assertEqual(
            response.data,
            {
                "id": str(bike.id),
                "station": {
                    "id": str(station.id),
                    "name": station.name,
                },
                "user": None,
                "status": BikeStatus.available,
            },
        )


class BikeDeleteTestCase(TestCase):
    def test_delete_bike_successful_status_code(self):
        bike = Bike.objects.create()
        response = self.client.delete(reverse("bike-detail", kwargs={"pk": bike.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_bike_successful_body(self):
        bike = Bike.objects.create()
        response = self.client.delete(reverse("bike-detail", kwargs={"pk": bike.id}))
        self.assertEqual(response.data, None)

    def test_delete_bike_successful_doesnt_exist(self):
        bike = Bike.objects.create()
        self.client.delete(reverse("bike-detail", kwargs={"pk": bike.id}))
        self.assertFalse(Bike.objects.filter(id=bike.id).exists())


class BikesGetRentedTestCase(TestCase):
    def test_get_rented_bikes_status_code(self):
        response = self.client.get(reverse("bikes-rented-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bikes_body(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name")
        Bike.objects.create(user=user, station=station, status=BikeStatus.available)
        bike1 = Bike.objects.create(
            user=user, station=station, status=BikeStatus.rented
        )
        bike2 = Bike.objects.create(
            user=user, station=station, status=BikeStatus.rented
        )
        Bike.objects.create(user=user, station=station, status=BikeStatus.available)
        response = self.client.get(reverse("bikes-rented-list"))
        self.assertEqual(
            response.data,
            [
                {
                    "id": str(bike1.id),
                    "station": {
                        "id": str(bike1.station.id),
                        "name": bike1.station.name,
                    },
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike1.status,
                },
                {
                    "id": str(bike2.id),
                    "station": {
                        "id": str(bike2.station.id),
                        "name": bike2.station.name,
                    },
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike2.status,
                },
            ],
        )


class BikesRentTestCase(TestCase):
    def test_rent_bike_status_code(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rent_bike_body(self):
        user = User.objects.create(first_name="John2", last_name="Doe")
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(
            response.data,
            {
                "id": str(rented_bike.id),
                "station": {
                    "id": str(rented_bike.station.id),
                    "name": rented_bike.station.name,
                },
                "user": {"id": str(user.id), "name": user.name},
                "status": BikeStatus.rented,
            },
        )

    def test_rent_bike_user_blocked(self):
        pass

    def test_rent_bike_blocked(self):
        user = User.objects.create(first_name="John3", last_name="Doe")
        station = Station.objects.create(name="Station Name already blocked")
        rented_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.blocked
        )
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_already_rented(self):
        user = User.objects.create(first_name="John4", last_name="Doe")
        station = Station.objects.create(name="Station Name already rented")
        rented_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_already_reserved(self):
        user = User.objects.create(first_name="John5", last_name="Doe")
        station = Station.objects.create(name="Station Name already reserved")
        rented_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.reserved
        )
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_station_blocked(self):
        user = User.objects.create(first_name="John4", last_name="Doe")
        station = Station.objects.create(
            name="Station Name already rented", state=StationState.blocked
        )
        rented_bike = Bike.objects.create(
            user=user, station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
