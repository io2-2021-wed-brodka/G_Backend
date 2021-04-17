from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bikes.models import Bike, BikeStatus
from bikes.serializers import (
    ReadBikeSerializer,
    CreateBikeSerializer,
    RentBikeSerializer,
)
from stations.models import Station, StationState


class BikeViewSet(ModelViewSet):
    queryset = Bike.objects.filter(status=BikeStatus.available)

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
    queryset = Bike.objects.filter(status=BikeStatus.rented)

    def get_serializer_class(self):
        if self.action == "create":
            return RentBikeSerializer
        else:
            return ReadBikeSerializer

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
        try:
            Station.objects.get(id=rented_bike.station.id, state=StationState.blocked)
        except Station.DoesNotExist:
            if not rented_bike.status == BikeStatus.available:
                return Response(
                    {
                        "message": "Bike is not available, it is rented, blocked or reserved"
                    },
                    status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                )
            rented_bike.status = BikeStatus.rented
            return Response(
                data=ReadBikeSerializer(rented_bike).data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response(
            {"message": "Bike is not available, it is rented, blocked or reserved"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
