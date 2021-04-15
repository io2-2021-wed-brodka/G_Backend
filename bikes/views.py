from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response

from bikes.models import Bike, BikeStatus
from bikes.serializers import ReadBikeSerializer, CreateBikeSerializer
from stations.models import Station, StationState


class BikeViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    queryset = Bike.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBikeSerializer
        else:
            return ReadBikeSerializer

    def create(self, request, *args, **kwargs):
        # we override the whole CreateModelMixin.create, because we need to keep created object
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bike = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            data=ReadBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class RentedBikesViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    queryset = Bike.objects.filter(status=BikeStatus.in_service)
    serializer_class = ReadBikeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        headers = self.get_success_headers(serializer.data)
        try:
            rented_bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "bike not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if rented_bike.user.username == "blocked":  # placeholder user is blocked
            return Response(
                {"message": "Blocked users are not allowed to rent bikes"},
                status=status.HTTP_403_FORBIDDEN,
            )
        if Station.objects.exists(
            id=rented_bike.station.id, status=StationState.blocked
        ):  # blocked station
            return Response(
                {
                    "message": "Station is blocked, it is not possible to rent bike from blocked station"
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if not rented_bike.status == BikeStatus.working:
            return Response(
                {"message": "Bike is not available, it is rented, blocked or reserved"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        rented_bike.status = BikeStatus.rented  # should be rented
        return Response(
            data=ReadBikeSerializer(rented_bike).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )
