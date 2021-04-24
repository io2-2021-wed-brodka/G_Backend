from django.utils import timezone
from core.testcases import APITestCase

from rest_framework.reverse import reverse
from rest_framework import status

from bikes.models import Bike, BikeStatus, Reservation
from stations.models import Station, StationState
from users.models import User


class BikesGetTestCase(APITestCase):
    def test_get_bikes_status_code(self):
        response = self.client.get(reverse("bike-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bikes_body(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station1 = Station.objects.create(name="Station Name 1")
        station2 = Station.objects.create(name="Station Name 2")
        bike1 = Bike.objects.create(status=BikeStatus.rented, user=user)
        bike2 = Bike.objects.create(station=station1)
        bike3 = Bike.objects.create(status=BikeStatus.reserved, station=station2)
        response = self.client.get(reverse("bike-list"))
        self.assertListEqual(
            response.data,
            [
                {
                    "id": str(bike1.id),
                    "station": None,
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike1.status,
                },
                {
                    "id": str(bike2.id),
                    "station": {
                        "id": str(bike2.station.id),
                        "name": bike2.station.name,
                        "activeBikesCount": bike2.station.bikes.count(),
                    },
                    "user": None,
                    "status": bike2.status,
                },
                {
                    "id": str(bike3.id),
                    "station": {
                        "id": str(bike3.station.id),
                        "name": bike3.station.name,
                        "activeBikesCount": bike3.station.bikes.count(),
                    },
                    "user": None,
                    "status": bike3.status,
                },
            ],
        )


class BikeCreateTestCase(APITestCase):
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
                    "activeBikesCount": station.bikes.count(),
                },
                "user": None,
                "status": BikeStatus.available,
            },
        )


class BikeDeleteTestCase(APITestCase):
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


class BikesGetRentedTestCase(APITestCase):
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
                        "activeBikesCount": bike1.station.bikes.count(),
                    },
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike1.status,
                },
                {
                    "id": str(bike2.id),
                    "station": {
                        "id": str(bike2.station.id),
                        "name": bike2.station.name,
                        "activeBikesCount": bike2.station.bikes.count(),
                    },
                    "user": {"id": str(user.id), "name": user.name},
                    "status": bike2.status,
                },
            ],
        )


class BikesRentTestCase(APITestCase):
    def test_rent_bike_status_code(self):
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_rent_bike_body(self):
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(
            response.data,
            {
                "id": str(rented_bike.id),
                "station": None,
                "user": {"id": str(self.user.id), "name": self.user.name},
                "status": BikeStatus.rented,
            },
        )

    def test_rent_bike_fail_user_blocked_status_code(self):
        self.user.block()
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_rent_bike_fails_bike_blocked(self):
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_fails_bike_already_rented(self):
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.rented)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_already_reserved(self):
        station = Station.objects.create(name="Station Name")
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_station_blocked(self):
        station = Station.objects.create(
            name="Station Name", state=StationState.blocked
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_status_changes_to_rented(self):
        station = Station.objects.create(
            name="Station Name already rented x", state=StationState.working
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        self.client.post(reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"})
        new_bike = Bike.objects.get(id=rented_bike.id)
        self.assertEqual(new_bike.status, BikeStatus.rented)

    def test_rent_bike_station_changes_to_null(self):
        station = Station.objects.create(
            name="Station Name already rented x", state=StationState.working
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        self.client.post(reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"})
        new_bike = Bike.objects.get(id=rented_bike.id)
        self.assertEqual(new_bike.station, None)


class BikeReservationTestCase(APITestCase):
    def test_create_reservation(self):
        station = Station.objects.create(name="Station Name")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-reserved-list"), {"id": reserved_bike.id}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_reservation_bike_status(self):
        station = Station.objects.create(name="Station Name")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        self.client.post(reverse("bikes-reserved-list"), {"id": reserved_bike.id})
        reserved_bike.refresh_from_db()
        self.assertEqual(reserved_bike.status, BikeStatus.reserved)

    def test_create_reservation_body(self):
        station = Station.objects.create(name="Station Name")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-reserved-list"), {"id": reserved_bike.id}
        )
        self.assertEqual(
            response.data,
            {
                "id": str(reserved_bike.id),
                "station": {
                    "id": str(reserved_bike.station.id),
                    "name": reserved_bike.station.name,
                    "activeBikesCount": reserved_bike.station.bikes.count(),
                },
                "reservedAt": reserved_bike.reservation.reserved_at,
                "reservedTill": reserved_bike.reservation.reserved_till,
            },
        )

    def test_create_reservation_reservation_added_to_db(self):
        station = Station.objects.create(name="Station Name create reservation body")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        self.client.post(reverse("bikes-reserved-list"), {"id": reserved_bike.id})
        reservation = reserved_bike.reservation
        self.assertIsNotNone(reservation)
        self.assertEqual(reservation.user, self.user)

    def test_create_reservation_fails_reservation_already_exist(self):
        station = Station.objects.create(name="Station Name reservation already exists")
        reserved_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        response = self.client.post(
            reverse("bikes-reserved-list"), {"id": reserved_bike.id}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_create_reservation_fails_user_blocked_status_code(self):
        self.user.block()
        station = Station.objects.create(name="Station Name reservation already exists")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-reserved-list"), {"id": reserved_bike.id}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_reservation_fails_user_blocked_body(self):
        self.user.block()
        station = Station.objects.create(name="Station Name reservation already exists")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        response = self.client.post(
            reverse("bikes-reserved-list"), {"id": reserved_bike.id}
        )
        self.assertDictEqual(
            response.data, {"message": "Blocked users are not allowed to rent bikes."}
        )


class BikeReservationDeleteTestCase(APITestCase):
    def test_delete_reservation_status_code(self):
        station = Station.objects.create(name="Station Name delete reservation")
        reserved_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        time = timezone.now()
        reservation = Reservation.objects.create(
            bike=reserved_bike,
            user=self.user,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )
        reserved_bike.reservation = reservation
        reserved_bike.save()
        response = self.client.delete(
            reverse("bikes-reserved-detail", kwargs={"pk": str(reserved_bike.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_reservation_bike_status(self):
        station = Station.objects.create(
            name="Station Name delete reservation bike status"
        )
        reserved_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        time = timezone.now()
        reservation = Reservation.objects.create(
            bike=reserved_bike,
            user=self.user,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )
        reserved_bike.reservation = reservation
        reserved_bike.save()
        self.client.delete(
            reverse("bikes-reserved-detail", kwargs={"pk": str(reserved_bike.id)})
        )
        reserved_bike.refresh_from_db()
        self.assertEqual(reserved_bike.status, BikeStatus.available)

    def test_delete_reservation_body(self):
        station = Station.objects.create(name="Station Name delete reservation body")
        reserved_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        time = timezone.now()
        reservation = Reservation.objects.create(
            bike=reserved_bike,
            user=self.user,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )
        reserved_bike.reservation = reservation
        reserved_bike.save()
        response = self.client.delete(
            reverse("bikes-reserved-detail", kwargs={"pk": str(reserved_bike.id)})
        )
        self.assertEqual(
            response.data,
            None,
        )

    def test_delete_reservation_bike_not_reserved(self):
        station = Station.objects.create(
            name="Station Name delete reservation bike not reserved"
        )
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        response = self.client.delete(
            reverse("bikes-reserved-detail", kwargs={"pk": str(reserved_bike.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
