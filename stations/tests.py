from rest_framework import status
from rest_framework.reverse import reverse

from bikes.models import Bike, BikeStatus
from core.testcases import APITestCase
from stations.models import Station, StationState
from users.models import User


class StationCreateTestCase(APITestCase):
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
        self.assertEqual(
            response.data,
            {
                "id": str(station.id),
                "name": station.name,
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
                        "activeBikesCount": station1.bikes.count(),
                    },
                    {
                        "id": str(station2.id),
                        "name": station2.name,
                        "activeBikesCount": station2.bikes.count(),
                    },
                    {
                        "id": str(station3.id),
                        "name": station3.name,
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


class StationBlockTestCase(APITestCase):
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
                        "activeBikesCount": station1.bikes.count(),
                    },
                    {
                        "id": str(station2.id),
                        "name": station2.name,
                        "activeBikesCount": station2.bikes.count(),
                    },
                ],
            },
        )
