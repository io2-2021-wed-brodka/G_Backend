from django.http import Http404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from bikes.models import Bike, BikeStatus, Reservation

from bikes.serializers import (
    ReadBikeSerializer,
    CreateBikeSerializer,
    RentBikeSerializer,
    ReserveBikeSerializer,
    ReserveIdSerializer,
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
    serializer_class = ReadBikeSerializer

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
        # TODO(kkrolik): uncomment once blocking users is introduced
        # user = somehow_get_user_from_token_in_headers(request)
        # if user.status == UserStatus.blocked:
        #     return Response(
        #         {"message": "Blocked users are not allowed to rent bikes"},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
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
            rented_bike.station = None
            rented_bike.save()
            return Response(
                data=ReadBikeSerializer(rented_bike).data,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        return Response(
            {"message": "Bike is not available, it is rented, blocked or reserved"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )


class ReservationsViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.filter(status=BikeStatus.reserved)
    serializer_class = ReserveBikeSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return ReserveIdSerializer
        else:
            return ReserveBikeSerializer

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(
                {"message": "Bike not reserved"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return super().handle_exception(exc)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            reserved_bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if (
            reserved_bike.status != BikeStatus.available
            or reserved_bike.station.state == StationState.blocked
        ):
            return Response(
                {
                    "message": "Bike already blocked, rented or reserved, or station is blocked"
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        # TODO(kboryczka): uncomment once blocking users is introduced
        # user = somehow_get_user_from_token_in_headers(request)
        # if user.status == UserStatus.blocked:
        #     return Response(
        #         {"message": "User is blocked"},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
        time = timezone.now()
        Reservation.objects.create(
            bike=reserved_bike,
            reserved_at=time,
            reserved_till=time + timezone.timedelta(minutes=30),
        )

        reserved_bike.status = BikeStatus.reserved
        reserved_bike.save()
        return Response(
            data=ReserveBikeSerializer(reserved_bike).data,
            status=status.HTTP_201_CREATED,
        )

    def destroy(self, request, *args, **kwargs):
        reserved_bike = self.get_object()
        if reserved_bike.status != BikeStatus.reserved:
            return Response(
                {"message": "Bike not reserved"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        reserved_bike = self.get_object()
        reserved_bike.reservation.delete()

        reserved_bike.status = BikeStatus.available
        reserved_bike.save()
        return Response(
            data=ReserveBikeSerializer(reserved_bike).data,
            status=status.HTTP_200_OK,
        )
