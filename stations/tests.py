from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse

from bikes.models import Bike, BikeStatus, Reservation
from core.testcases import APITestCase
from stations.models import Station, StationState
from users.models import User


class StationCreateTestCase(APITestCase):
    def test_create_station_status_code(self):
        response = self.client.post(
            reverse("station-list"), {"name": "Good 'ol station", "bikeLimit": 10}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_station_body(self):
        response = self.client.post(
            reverse("station-list"), {"name": "Good 'ol station", "bikeLimit": 10}
        )
        station = Station.objects.first()
        self.assertEqual(
            response.data,
            {
                "id": str(station.id),
                "name": station.name,
                "state": station.state,
                "activeBikesCount": station.bikes.count(),
            },
        )


class StationGetTestCase(APITestCase):
    def test_get_station_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_station_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.get(reverse("station-detail", kwargs={"pk": station.id}))
        self.assertEqual(
            response.data,
            {
                "id": str(station.id),
                "name": station.name,
                "state": station.state,
                "activeBikesCount": station.bikes.count(),
            },
        )


class StationListGetTestCase(APITestCase):
    def test_get_stations_status_code(self):
        response = self.client.get(reverse("station-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_stations_body(self):
        station1 = Station.objects.create(name="Good 'ol station 1")
        station2 = Station.objects.create(name="Good 'ol station 2")
        station3 = Station.objects.create(
            name="Good 'ol station 1", state=StationState.blocked
        )
        response = self.client.get(reverse("station-list"))
        self.assertDictEqual(
            response.data,
            {
                "stations": [
                    {
                        "id": str(station1.id),
                        "name": station1.name,
                        "state": station1.state,
                        "activeBikesCount": station1.bikes.count(),
                    },
                    {
                        "id": str(station2.id),
                        "name": station2.name,
                        "state": station2.state,
                        "activeBikesCount": station2.bikes.count(),
                    },
                    {
                        "id": str(station3.id),
                        "name": station3.name,
                        "state": station3.state,
                        "activeBikesCount": station3.bikes.count(),
                    },
                ],
            },
        )


class StationDeleteTestCase(APITestCase):
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
        self.assertEqual(response.data, {"message": "Station has bikes."})

    def test_delete_station_not_found_status_code(self):
        response = self.client.delete(reverse("station-detail", kwargs={"pk": "abc"}))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_station_not_found_body(self):
        response = self.client.delete(reverse("station-detail", kwargs={"pk": "abc"}))
        self.assertEqual(response.data, {"message": "Station not found."})


class StationListBlockedTestCase(APITestCase):
    def test_get_stations_status_code(self):
        response = self.client.get(reverse("stations-blocked-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_stations_body(self):
        station1 = Station.objects.create(
            name="Good 'ol station 1", state=StationState.blocked
        )
        station2 = Station.objects.create(
            name="Good 'ol station 2", state=StationState.blocked
        )
        Station.objects.create(name="Good 'ol station 3")
        response = self.client.get(reverse("stations-blocked-list"))
        self.assertDictEqual(
            response.data,
            {
                "stations": [
                    {
                        "id": str(station1.id),
                        "name": station1.name,
                        "state": station1.state,
                        "activeBikesCount": station1.bikes.count(),
                    },
                    {
                        "id": str(station2.id),
                        "name": station2.name,
                        "state": station2.state,
                        "activeBikesCount": station2.bikes.count(),
                    },
                ],
            },
        )


class StationBlockTestCase(APITestCase):
    def test_block_station_successful_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.post(
            reverse("stations-blocked-list"), {"id": f"{station.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_block_station_successful_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.post(
            reverse("stations-blocked-list"), {"id": f"{station.id}"}
        )
        self.assertEqual(
            response.data,
            {
                "id": str(station.id),
                "name": str(station.name),
                "state": "blocked",
                "activeBikesCount": 0,
            },
        )

    def test_block_station_gets_blocked(self):
        station = Station.objects.create(name="Good 'ol station")
        self.client.post(reverse("stations-blocked-list"), {"id": f"{station.id}"})
        station.refresh_from_db()
        self.assertEqual(station.state, StationState.blocked)

    def test_block_station_fails_not_found(self):
        station = Station.objects.create(name="Good 'ol station")
        delete_id = station.id
        Station.objects.filter(id=station.id).delete()
        response = self.client.post(
            reverse("stations-blocked-list"), {"id": f"{delete_id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_block_station_fails_already_blocked(self):
        station = Station.objects.create(
            name="Good 'ol station", state=StationState.blocked
        )
        response = self.client.post(
            reverse("stations-blocked-list"), {"id": f"{station.id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_cancel_reservations_after_block_bike_status(self):
        station = Station.objects.create(name="Good 'ol station")
        Bike.objects.create(station=station)
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
        self.client.post(reverse("stations-blocked-list"), {"id": f"{station.id}"})
        self.assertEqual(
            Bike.objects.get(id=reserved_bike.id).status, BikeStatus.available
        )

    def test_cancel_reservations_after_block_reservation_gets_deleted(self):
        station = Station.objects.create(name="Good 'ol station")
        Bike.objects.create(station=station)
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
        self.client.post(reverse("stations-blocked-list"), {"id": f"{station.id}"})
        self.assertFalse(Reservation.objects.filter(id=reservation.id).exists())


class StationBlockedListTestCase(APITestCase):
    def test_list_blocked_stations_status_code(self):
        response = self.client.get(reverse("stations-blocked-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_stations_body(self):
        Station.objects.create(name="Good 'ol station 1")
        station1 = Station.objects.create(
            name="Good 'ol station 2", state=StationState.blocked
        )
        station2 = Station.objects.create(
            name="Good 'ol station 3", state=StationState.blocked
        )
        Station.objects.create(name="Good 'ol station 4")
        response = self.client.get(reverse("stations-blocked-list"))
        self.assertDictEqual(
            response.data,
            {
                "stations": [
                    {
                        "id": str(station1.id),
                        "name": station1.name,
                        "state": station1.state,
                        "activeBikesCount": station1.bikes.count(),
                    },
                    {
                        "id": str(station2.id),
                        "name": station2.name,
                        "state": station2.state,
                        "activeBikesCount": station2.bikes.count(),
                    },
                ],
            },
        )


class StationUnblockTestCase(APITestCase):
    def test_unblock_station_successful_status_code(self):
        station = Station.objects.create(
            name="Good 'ol station", state=StationState.blocked
        )
        response = self.client.delete(
            reverse("stations-blocked-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_unblock_station_body(self):
        station = Station.objects.create(
            name="Good 'ol station", state=StationState.blocked
        )
        response = self.client.delete(
            reverse("stations-blocked-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.data, None)

    def test_unblock_station_station_gets_unblocked(self):
        station = Station.objects.create(
            name="Good 'ol station", state=StationState.blocked
        )
        self.client.delete(
            reverse("stations-blocked-detail", kwargs={"pk": station.id})
        )
        station.refresh_from_db()
        self.assertEqual(station.state, StationState.working)

    def test_unblock_station_fails_already_unblocked_status_code(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.delete(
            reverse("stations-blocked-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_unblock_station_fails_already_unblocked_body(self):
        station = Station.objects.create(name="Good 'ol station")
        response = self.client.delete(
            reverse("stations-blocked-detail", kwargs={"pk": station.id})
        )
        self.assertEqual(response.data, {"message": "Station not blocked."})


class StationReturnBikeTestCase(APITestCase):
    def test_return_bike_successful_status_code(self):
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=self.user, station=None, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_return_bike_successful_body(self):
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=self.user, station=None, status=BikeStatus.rented
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
                    "state": station.state,
                    "activeBikesCount": station.bikes.count(),
                },
                "user": None,
                "status": BikeStatus.available,
            },
        )

    def test_return_bike_not_found(self):
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=self.user, station=None, status=BikeStatus.rented
        )
        delete_id = returned_bike.id
        Bike.objects.filter(id=returned_bike.id).delete()
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}), {"id": f"{delete_id}"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_bike_station_not_none(self):
        station = Station.objects.create(
            name="Station Name", state=StationState.working
        )
        returned_bike = Bike.objects.create(
            user=self.user, station=station, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_return_bike_fails_station_blocked(self):
        station = Station.objects.create(
            name="Station Name", state=StationState.blocked
        )
        returned_bike = Bike.objects.create(
            user=self.user, station=None, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

    def test_return_bike_fails_station_over_capacity(self):
        station = Station.objects.create(name="Station Name", capacity=0)
        returned_bike = Bike.objects.create(
            user=self.user, station=None, status=BikeStatus.rented
        )
        response = self.client.post(
            reverse("station-bikes", kwargs={"pk": station.id}),
            {"id": f"{returned_bike.id}"},
        )
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(
            response.data,
            {
                "message": "Cannot associate specified bike with specified station, station is full."
            },
        )

    def test_return_bike_fails_user_returning_is_different(self):
        user = User.objects.create(first_name="John", last_name="Doe")
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
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertDictEqual(
            response.data,
            {"message": "User returning the bike is not the user that rented it."},
        )


class ListBikesAtStationTestCase(APITestCase):
    def test_list_bikes_at_station_status_code(self):
        response = self.client.get(reverse("station-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_bikes_at_station_body(self):
        station1 = Station.objects.create(name="Station Name 1")
        station2 = Station.objects.create(name="Station Name 2")
        Bike.objects.create(status=BikeStatus.rented, user=self.user)
        bike1 = Bike.objects.create(station=station1)
        bike2 = Bike.objects.create(station=station1)
        Bike.objects.create(station=station2)
        Bike.objects.create(status=BikeStatus.reserved, station=station2)
        response = self.client.get(reverse("station-bikes", kwargs={"pk": station1.id}))
        self.assertDictEqual(
            response.data,
            {
                "bikes": [
                    {
                        "id": str(bike1.id),
                        "station": {
                            "id": str(bike1.station.id),
                            "name": bike1.station.name,
                            "state": bike1.station.state,
                            "activeBikesCount": bike1.station.bikes.count(),
                        },
                        "user": None,
                        "status": bike1.status,
                    },
                    {
                        "id": str(bike2.id),
                        "station": {
                            "id": str(bike2.station.id),
                            "name": bike2.station.name,
                            "state": bike2.station.state,
                            "activeBikesCount": bike2.station.bikes.count(),
                        },
                        "user": None,
                        "status": bike2.status,
                    },
                ],
            },
        )


class ActiveStationListGetTestCase(APITestCase):
    def test_get_active_stations_status_code(self):
        response = self.client.get(reverse("station-active"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_active_stations_body(self):
        station1 = Station.objects.create(name="Good 'ol station 1")
        station2 = Station.objects.create(name="Good 'ol station 2")
        Station.objects.create(name="Good 'ol station 3", state=StationState.blocked)
        response = self.client.get(reverse("station-active"))
        self.assertDictEqual(
            response.data,
            {
                "stations": [
                    {
                        "id": str(station1.id),
                        "name": station1.name,
                        "state": station1.state,
                        "activeBikesCount": station1.bikes.count(),
                    },
                    {
                        "id": str(station2.id),
                        "name": station2.name,
                        "state": station2.state,
                        "activeBikesCount": station2.bikes.count(),
                    },
                ],
            },
        )
