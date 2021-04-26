from django.http import Http404
from rest_framework import status, mixins
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bikes.models import Bike, BikeStatus
from bikes.serializers import ReadBikeSerializer
from core.decorators import restrict
from stations.models import Station, StationState
from stations.serializers import StationSerializer
from users.models import UserRole


class StationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(
                {"message": "Station not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        return super().handle_exception(exc)

    @restrict(UserRole.admin)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @restrict(UserRole.admin, UserRole.tech)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @restrict(UserRole.admin, UserRole.tech)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        """
        Delete a station.

        Conditions:
        - Station can't contain bikes
        """
        station = self.get_object()
        if station.bikes.exists():
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={"message": "Station has bikes."},
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    @restrict(UserRole.admin)
    def blocked(self, request, *args, **kwargs):
        """
        Block a station.
        Station id is provided in body.

        Conditions:
        - Station must exist
        - Station must be currently working
        """
        try:
            station = Station.objects.get(id=request.data.get("id"))
        except Station.DoesNotExist:
            return Response(
                {"message": "Station not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if station.state != StationState.working:
            return Response(
                {"message": "Station already blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        station.block()
        return Response(
            {"id": str(station.id), "name": station.name},
            status=status.HTTP_201_CREATED,
        )

    @action(detail=True, methods=["get", "post"])
    @restrict(UserRole.admin, UserRole.tech, UserRole.user)
    def bikes(self, request, *args, **kwargs):
        if request.method == "GET":
            return self.list_bikes_at_station(request, *args, **kwargs)
        else:
            return self.return_bike_to_station(request, *args, **kwargs)

    def list_bikes_at_station(self, request, *args, **kwargs):
        station = self.get_object()
        bikes = station.bikes.filter(status=BikeStatus.available)
        return Response(
            status=status.HTTP_200_OK,
            data=ReadBikeSerializer(bikes, many=True).data,
        )

    def return_bike_to_station(self, request, *args, **kwargs):
        """
        Rent out a bike.
        Bike id is provided in body.

        Conditions:
        - Bike with given id must exist
        - Bike must be rented
        - User returning the bike must be the user that rented the bike
        - Station can't be blocked
        - Station can't be over capacity
        """
        try:
            bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if bike.status != BikeStatus.rented or bike.station is not None:
            return Response(
                {"message": "Bike not rented."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if request.user != bike.user:
            return Response(
                {"message": "User returning the bike is not the user that rented it."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        station = self.get_object()
        if station.state == StationState.blocked:
            return Response(
                {
                    "message": "Cannot associate specified bike with specified station, station is blocked."
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if station.bikes.count() >= station.capacity:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={
                    "message": "Cannot associate specified bike with specified station, station is full."
                },
            )
        bike.return_to_station(station)

        return Response(
            data=ReadBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
        )
