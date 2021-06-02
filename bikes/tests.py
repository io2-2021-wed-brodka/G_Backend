from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from bikes.models import Bike, BikeStatus, Reservation, Malfunction
from core.testcases import APITestCase
from stations.models import Station, StationStatus
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
        self.assertDictEqual(
            response.data,
            {
                "bikes": [
                    {
                        "id": str(bike1.id),
                        "station": None,
                        "user": {"id": str(user.id), "name": user.username},
                        "status": bike1.status,
                    },
                    {
                        "id": str(bike2.id),
                        "station": {
                            "id": str(bike2.station.id),
                            "name": bike2.station.name,
                            "status": bike2.station.status,
                            "bikesLimit": bike2.station.bikesLimit,
                            "activeBikesCount": bike2.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "user": None,
                        "status": bike2.status,
                    },
                    {
                        "id": str(bike3.id),
                        "station": {
                            "id": str(bike3.station.id),
                            "name": bike3.station.name,
                            "status": bike3.station.status,
                            "bikesLimit": bike3.station.bikesLimit,
                            "activeBikesCount": bike3.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "user": None,
                        "status": bike3.status,
                    },
                ],
            },
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
                    "status": station.status,
                    "bikesLimit": station.bikesLimit,
                    "activeBikesCount": station.bikes.filter(
                        status=BikeStatus.available
                    ).count(),
                },
                "user": None,
                "status": BikeStatus.available,
            },
        )


class BikeDeleteTestCase(APITestCase):
    def test_delete_bike_successful_status_code(self):
        bike = Bike.objects.create(status=BikeStatus.blocked)
        response = self.client.delete(reverse("bike-detail", kwargs={"pk": bike.id}))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_bike_successful_body(self):
        bike = Bike.objects.create(status=BikeStatus.blocked)
        response = self.client.delete(reverse("bike-detail", kwargs={"pk": bike.id}))
        self.assertEqual(response.data, None)

    def test_delete_bike_successful_doesnt_exist(self):
        bike = Bike.objects.create(status=BikeStatus.blocked)
        self.client.delete(reverse("bike-detail", kwargs={"pk": bike.id}))
        self.assertFalse(Bike.objects.filter(id=bike.id).exists())


class BikesGetRentedTestCase(APITestCase):
    def test_get_rented_bikes_status_code(self):
        response = self.client.get(reverse("bikes-rented-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_bikes_body(self):
        station = Station.objects.create(name="Station Name")
        Bike.objects.create(station=station, status=BikeStatus.available)
        bike1 = Bike.objects.create(
            user=self.user, station=station, status=BikeStatus.rented
        )
        bike2 = Bike.objects.create(
            user=self.user, station=station, status=BikeStatus.rented
        )
        Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.get(reverse("bikes-rented-list"))
        self.assertDictEqual(
            response.data,
            {
                "bikes": [
                    {
                        "id": str(bike1.id),
                        "station": {
                            "id": str(bike1.station.id),
                            "name": bike1.station.name,
                            "status": bike1.station.status,
                            "bikesLimit": bike1.station.bikesLimit,
                            "activeBikesCount": bike1.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "user": {"id": str(self.user.id), "name": self.user.username},
                        "status": bike1.status,
                    },
                    {
                        "id": str(bike2.id),
                        "station": {
                            "id": str(bike2.station.id),
                            "name": bike2.station.name,
                            "status": bike2.station.status,
                            "bikesLimit": bike2.station.bikesLimit,
                            "activeBikesCount": bike2.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "user": {"id": str(self.user.id), "name": self.user.username},
                        "status": bike2.status,
                    },
                ],
            },
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
                "user": {"id": str(self.user.id), "name": self.user.username},
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
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name")
        bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        time = timezone.now()
        Reservation.objects.create(
            bike=bike,
            user=user,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )
        response = self.client.post(reverse("bikes-rented-list"), {"id": f"{bike.id}"})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_fails_station_blocked(self):
        station = Station.objects.create(
            name="Station Name", status=StationStatus.blocked
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_rent_bike_status_changes_to_rented(self):
        station = Station.objects.create(
            name="Station Name already rented x", status=StationStatus.working
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        self.client.post(reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"})
        new_bike = Bike.objects.get(id=rented_bike.id)
        self.assertEqual(new_bike.status, BikeStatus.rented)

    def test_rent_bike_station_changes_to_null(self):
        station = Station.objects.create(
            name="Station Name already rented x", status=StationStatus.working
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        self.client.post(reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"})
        rented_bike.refresh_from_db()
        self.assertEqual(rented_bike.station, None)

    def test_rent_bike_that_was_reserved(self):
        station = Station.objects.create(
            name="Station Name already rented x", status=StationStatus.working
        )
        reserved_bike = Bike.objects.create(station=station)
        reserved_bike.reserve(self.user)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{reserved_bike.id}"}
        )
        reserved_bike.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(reserved_bike.station, None)
        self.assertEqual(reserved_bike.user, self.user)
        self.assertFalse(hasattr(reserved_bike, "reservation"))

    def test_rent_bike_fails_user_over_rental_limit(self):
        self.user.rental_limit = 0
        self.user.save()
        station = Station.objects.create(
            name="Station Name already rented x", status=StationStatus.working
        )
        rented_bike = Bike.objects.create(station=station, status=BikeStatus.available)
        response = self.client.post(
            reverse("bikes-rented-list"), {"id": f"{rented_bike.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {"message": "User reached rental limit of 0."})


class BikesGetReservedTestCase(APITestCase):
    def test_get_reserved_bikes_status_code(self):
        response = self.client.get(reverse("bikes-reserved-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_reserved_bikes_body(self):
        other_user = User.objects.create(first_name="John", last_name="Doe")
        station1 = Station.objects.create(name="Station Name 1")
        station2 = Station.objects.create(name="Station Name 2")
        bike1 = Bike.objects.create(station=station1)
        bike1.reserve(self.user)
        bike2 = Bike.objects.create(station=station2)
        bike2.reserve(self.user)
        Bike.objects.create(station=station2)
        bike3 = Bike.objects.create(station=station2)
        bike3.reserve(other_user)

        response = self.client.get(reverse("bikes-reserved-list"))
        self.assertDictEqual(
            response.data,
            {
                "bikes": [
                    {
                        "id": str(bike1.id),
                        "station": {
                            "id": str(bike1.station.id),
                            "name": bike1.station.name,
                            "status": bike1.station.status,
                            "bikesLimit": bike1.station.bikesLimit,
                            "activeBikesCount": bike1.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "reservedAt": bike1.reservation.reserved_at,
                        "reservedTill": bike1.reservation.reserved_till,
                    },
                    {
                        "id": str(bike2.id),
                        "station": {
                            "id": str(bike2.station.id),
                            "name": bike2.station.name,
                            "status": bike2.station.status,
                            "bikesLimit": bike2.station.bikesLimit,
                            "activeBikesCount": bike2.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "reservedAt": bike2.reservation.reserved_at,
                        "reservedTill": bike2.reservation.reserved_till,
                    },
                ]
            },
        )


class BikeMakeReservationTestCase(APITestCase):
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
                    "status": reserved_bike.station.status,
                    "bikesLimit": reserved_bike.station.bikesLimit,
                    "activeBikesCount": reserved_bike.station.bikes.filter(
                        status=BikeStatus.available
                    ).count(),
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

    def test_create_reservation_fails_user_has_max_reservations(self):
        station = Station.objects.create(name="Station Name reservation already exists")
        reserved_bike = Bike.objects.create(
            station=station, status=BikeStatus.available
        )
        Bike.objects.create(station=station, status=BikeStatus.available).reserve(
            self.user
        )
        Bike.objects.create(station=station, status=BikeStatus.available).reserve(
            self.user
        )
        Bike.objects.create(station=station, status=BikeStatus.available).reserve(
            self.user
        )
        response = self.client.post(
            reverse("bikes-reserved-list"), {"id": reserved_bike.id}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertDictEqual(
            response.data, {"message": "User already has max reservations."}
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

    def test_delete_reservation_fails_user_cancelling_reservation_is_different(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name delete reservation body")
        reserved_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        time = timezone.now()
        Reservation.objects.create(
            bike=reserved_bike,
            user=user,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )
        response = self.client.delete(
            reverse("bikes-reserved-detail", kwargs={"pk": str(reserved_bike.id)})
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.data,
            {
                "message": "User cancelling the reservation is not the user that reserved it."
            },
        )


class BikeReservationExpiresTestCase(APITestCase):
    def test_reservation_expires(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station = Station.objects.create(name="Station Name delete reservation body")
        reserved_bike = Bike.objects.create(station=station, status=BikeStatus.reserved)
        time = timezone.now()
        Reservation.objects.create(
            bike=reserved_bike,
            user=user,
            reserved_at=time,
            reserved_till=time,
        )
        self.assertEqual(reserved_bike.status, BikeStatus.reserved)
        self.client.get(reverse("bike-list"))
        reserved_bike.refresh_from_db()
        self.assertEqual(reserved_bike.status, BikeStatus.available)


class BikeListBlockedTestCase(APITestCase):
    def test_get_blocked_bikes_status_code(self):
        response = self.client.get(reverse("bikes-blocked-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_blocked_bikes_body(self):
        user = User.objects.create(first_name="John", last_name="Doe")
        station1 = Station.objects.create(name="Station Name 1")
        station2 = Station.objects.create(name="Station Name 2")
        bike1 = Bike.objects.create(station=station1, status=BikeStatus.blocked)
        bike2 = Bike.objects.create(station=station2, status=BikeStatus.blocked)
        Bike.objects.create(status=BikeStatus.rented, user=user)
        Bike.objects.create(station=station1)
        Bike.objects.create(status=BikeStatus.reserved, station=station2)
        response = self.client.get(reverse("bikes-blocked-list"))
        self.assertDictEqual(
            response.data,
            {
                "bikes": [
                    {
                        "id": str(bike1.id),
                        "station": {
                            "id": str(bike1.station.id),
                            "name": bike1.station.name,
                            "status": bike1.station.status,
                            "bikesLimit": bike1.station.bikesLimit,
                            "activeBikesCount": bike1.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "user": None,
                        "status": BikeStatus.blocked,
                    },
                    {
                        "id": str(bike2.id),
                        "station": {
                            "id": str(bike2.station.id),
                            "name": bike2.station.name,
                            "status": bike2.station.status,
                            "bikesLimit": bike2.station.bikesLimit,
                            "activeBikesCount": bike2.station.bikes.filter(
                                status=BikeStatus.available
                            ).count(),
                        },
                        "user": None,
                        "status": BikeStatus.blocked,
                    },
                ],
            },
        )


class BikeBlockTestCase(APITestCase):
    def test_block_bike_successful_status_code(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station)
        response = self.client.post(reverse("bikes-blocked-list"), {"id": f"{bike.id}"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_block_bike_successful_body(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station)
        response = self.client.post(reverse("bikes-blocked-list"), {"id": f"{bike.id}"})
        self.assertEqual(
            response.data,
            {
                "id": str(bike.id),
                "station": {
                    "id": str(bike.station.id),
                    "name": bike.station.name,
                    "status": bike.station.status,
                    "bikesLimit": bike.station.bikesLimit,
                    "activeBikesCount": bike.station.bikes.filter(
                        status=BikeStatus.available
                    ).count(),
                },
                "user": None,
                "status": BikeStatus.blocked,
            },
        )

    def test_block_bike_gets_blocked(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station)
        self.client.post(reverse("bikes-blocked-list"), {"id": f"{bike.id}"})
        bike.refresh_from_db()
        self.assertEqual(bike.status, BikeStatus.blocked)

    def test_block_bike_fails_not_found(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        delete_id = bike.id
        Bike.objects.filter(id=bike.id).delete()
        response = self.client.post(
            reverse("bikes-blocked-list"), {"id": f"{delete_id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_block_bike_fails_already_blocked(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        response = self.client.post(reverse("bikes-blocked-list"), {"id": f"{bike.id}"})
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)


class BikeUnblockTestCase(APITestCase):
    def test_unblock_bike_status_code(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        response = self.client.delete(
            reverse("bikes-blocked-detail", kwargs={"pk": bike.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unblock_bike_body(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        response = self.client.delete(
            reverse("bikes-blocked-detail", kwargs={"pk": bike.id})
        )
        self.assertEqual(response.data, None)

    def test_unblock_bike_bike_gets_unblocked(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        self.client.delete(reverse("bikes-blocked-detail", kwargs={"pk": bike.id}))
        bike.refresh_from_db()
        self.assertEqual(bike.status, BikeStatus.available)

    def test_unblock_bike_fails_already_unblocked_status_code(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station)
        response = self.client.delete(
            reverse("bikes-blocked-detail", kwargs={"pk": bike.id})
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_unblock_bike_fails_already_unblocked_body(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station)
        response = self.client.delete(
            reverse("bikes-blocked-detail", kwargs={"pk": bike.id})
        )
        self.assertEqual(response.data, {"message": "Bike not blocked."})

    def test_unblock_bike_fails_not_found(self):
        station = Station.objects.create(name="Station Name 1")
        bike = Bike.objects.create(station=station, status=BikeStatus.blocked)
        bike.refresh_from_db()
        delete_id = bike.id
        Bike.objects.filter(id=bike.id).delete()
        response = self.client.delete(
            reverse("bikes-blocked-detail", kwargs={"pk": delete_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {"message": "Bike does not exist."})


class MalfunctionListTestCase(APITestCase):
    def test_get_malfunctions_status_code(self):
        response = self.client.get(reverse("malfunction-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_malfunctions_body(self):
        user1 = User.objects.create(username="john-doe")
        user2 = User.objects.create(username="jack-black")
        bike1 = Bike.objects.create()
        bike1.rent(user1)
        bike2 = Bike.objects.create()
        bike2.rent(user2)
        malfunction1 = Malfunction.objects.create(bike=bike1, reporting_user=user1)
        malfunction2 = Malfunction.objects.create(bike=bike2, reporting_user=user2)
        response = self.client.get(reverse("malfunction-list"))
        self.assertDictEqual(
            response.data,
            {
                "malfunctions": [
                    {
                        "id": str(malfunction1.id),
                        "bikeId": str(malfunction1.bike.id),
                        "description": malfunction1.description,
                        "reportingUserId": str(malfunction1.reporting_user.id),
                    },
                    {
                        "id": str(malfunction2.id),
                        "bikeId": str(malfunction2.bike.id),
                        "description": malfunction2.description,
                        "reportingUserId": str(malfunction2.reporting_user.id),
                    },
                ],
            },
        )


class MalfunctionCreateTestCase(APITestCase):
    def test_create_malfunction_successful_status_code(self):
        bike = Bike.objects.create()
        bike.rent(self.user)
        response = self.client.post(
            reverse("malfunction-list"),
            {"id": str(bike.id), "description": "makes noises"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_malfunction_successful_body(self):
        bike = Bike.objects.create()
        bike.rent(self.user)
        response = self.client.post(
            reverse("malfunction-list"),
            {"id": str(bike.id), "description": "makes noises"},
        )
        self.assertEqual(
            response.data,
            {
                "id": str(bike.malfunction.id),
                "bikeId": str(bike.malfunction.bike.id),
                "description": bike.malfunction.description,
                "reportingUserId": str(bike.malfunction.reporting_user.id),
            },
        )

    def test_create_malfunction_fails_bike_not_found(self):
        bike = Bike.objects.create()
        bike_id = bike.id
        bike.delete()
        response = self.client.post(
            reverse("malfunction-list"),
            {"id": str(bike_id), "description": "makes noises"},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {"message": "Bike not found."})

    def test_create_malfunction_fails_wrong_user(self):
        user = User.objects.create(username="john-doe")
        bike = Bike.objects.create()
        bike.rent(user)
        response = self.client.post(
            reverse("malfunction-list"),
            {"id": str(bike.id), "description": "makes noises"},
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.data, {"message": "Bike not rented by reporting user."}
        )


class MalfunctionDestroyTestCase(APITestCase):
    def test_destroy_malfunction_status_code(self):
        bike = Bike.objects.create()
        bike.rent(self.user)
        malfunction = Malfunction.objects.create(bike=bike, reporting_user=self.user)
        response = self.client.delete(
            reverse("malfunction-detail", kwargs={"pk": malfunction.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_destroy_malfunction_body(self):
        bike = Bike.objects.create()
        bike.rent(self.user)
        malfunction = Malfunction.objects.create(bike=bike, reporting_user=self.user)
        response = self.client.delete(
            reverse("malfunction-detail", kwargs={"pk": malfunction.id})
        )
        self.assertEqual(response.data, None)

    def test_destroy_malfunction_malfunction_gets_destroyed(self):
        bike = Bike.objects.create()
        bike.rent(self.user)
        malfunction = Malfunction.objects.create(bike=bike, reporting_user=self.user)
        self.client.delete(reverse("malfunction-detail", kwargs={"pk": malfunction.id}))
        self.assertEqual(Malfunction.objects.filter(id=malfunction.id).first(), None)

    def test_destroy_malfunction_fails_not_found(self):
        bike = Bike.objects.create()
        bike.rent(self.user)
        malfunction = Malfunction.objects.create(bike=bike, reporting_user=self.user)
        delete_id = malfunction.id
        malfunction.delete()
        response = self.client.delete(
            reverse("malfunction-detail", kwargs={"pk": delete_id})
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual(response.data, {"message": "Malfunction does not exist."})
