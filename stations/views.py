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
    queryset = Station.objects.filter(state=StationState.working)
    serializer_class = StationSerializer

    @restrict(UserRole.admin)
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @restrict(UserRole.admin, UserRole.tech, UserRole.user)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @restrict(UserRole.admin, UserRole.tech, UserRole.user)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        try:
            station = self.get_object()
        except Http404:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "station not found"}
            )

        if station.bikes.exists():
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={"message": "station has bikes"},
            )
        return super().destroy(request, *args, **kwargs)

    @action(detail=False, methods=["post"])
    @restrict(UserRole.admin)
    def blocked(self, request, *args, **kwargs):
        try:
            station = Station.objects.get(id=request.data.get("id"))
        except Station.DoesNotExist:
            return Response(
                {"message": "station not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if station.state == StationState.working:
            station.state = StationState.blocked
            station.save()
            return Response(
                {"id": f"{station.id}", "name": f"{station.name}"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "station already blocked"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

    @action(detail=True, methods=["post"])
    def bikes(self, request, *args, **kwargs):  # return bikes
        try:
            bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found"}, status=status.HTTP_404_NOT_FOUND
            )
        station = Station.objects.get(id=kwargs["pk"])
        if station.state == StationState.blocked:
            return Response(
                {
                    "message": "Cannot associate specified bike with specified station, station is blocked"
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        # TODO(kkrolik): uncomment once capasity of station is introduced
        # capasity = 10
        # if Bike.objects.get(station=station.id).count() > capasity:
        #    return Response(
        #        {"message": "Cannot associate specified bike with specified station, station is full"},
        #        status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        #    )
        if bike.station is not None:
            return Response(
                {"message": "Bike associated to another station"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        bike.station = station
        bike.status = BikeStatus.available
        bike.user = None
        bike.save()

        return Response(
            data=ReadBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
        )
