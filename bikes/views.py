from django.http import Http404
from rest_framework import viewsets, status, mixins
from rest_framework.mixins import CreateModelMixin, ListModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bikes.models import Bike, BikeStatus

from bikes.serializers import (
    ReadBikeSerializer,
    CreateBikeSerializer,
    RentBikeSerializer,
    ReserveBikeSerializer,
    ReserveIdSerializer,
)
from core.decorators import restrict
from stations.models import Station, StationState
from users.models import UserRole


class BikeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Bike.objects.filter(status=BikeStatus.available)

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBikeSerializer
        else:
            return ReadBikeSerializer

    @restrict(UserRole.admin)
    def create(self, request, *args, **kwargs):
        # we override the whole CreateModelMixin.create, because we need to keep created object
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bike = serializer.save()
        return Response(
            data=ReadBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
        )

    @restrict(UserRole.tech, UserRole.admin)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RentedBikesViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    queryset = Bike.objects.filter(status=BikeStatus.rented)
    serializer_class = ReadBikeSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return RentBikeSerializer
        else:
            return ReadBikeSerializer

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rented_bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "bike not found"}, status=status.HTTP_404_NOT_FOUND
            )
        # TODO(kkrolik): uncomment once blocking users is introduced
        # if request.user.status == UserStatus.blocked:
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
            )
        return Response(
            {"message": "Bike is not available, it is rented, blocked or reserved"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ReservationsViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
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

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
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
        # TODO(kboryczka): uncomment once blocking of users is introduced
        # user = somehow_get_user_from_token_in_headers(request)
        # if user.status == UserStatus.blocked:
        #     return Response(
        #         {"message": "User is blocked"},
        #         status=status.HTTP_403_FORBIDDEN,
        #     )
        reserved_bike.reserve()
        return Response(
            data=ReserveBikeSerializer(reserved_bike).data,
            status=status.HTTP_201_CREATED,
        )

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        reserved_bike = self.get_object()
        if reserved_bike.status != BikeStatus.reserved:
            return Response(
                {"message": "Bike not reserved"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        reserved_bike.cancel_reservation()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
