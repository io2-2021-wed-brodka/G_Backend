from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
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
)
from core.decorators import restrict
from core.serializers import MessageSerializer
from stations.models import StationState
from users.models import UserRole, UserState


class BikeViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = Bike.objects.all()
    response_serializer = ReadBikeSerializer
    message_serializer = MessageSerializer

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBikeSerializer
        else:
            return ReadBikeSerializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response("Successful response", response_serializer),
            404: openapi.Response("Not found", message_serializer),
        }
    )
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
        return Response(
            status=status.HTTP_200_OK,
            data={"bikes": ReadBikeSerializer(self.get_queryset(), many=True).data},
        )

    @swagger_auto_schema(
        responses={
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Errors", message_serializer),
        }
    )
    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class RentedBikesViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
    request_serializer = RentBikeSerializer
    response_serializer = ReadBikeSerializer
    message_serializer = MessageSerializer

    def get_queryset(self):
        return Bike.objects.filter(status=BikeStatus.rented, user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return self.request_serializer
        else:
            return self.response_serializer

    @swagger_auto_schema(
        responses={
            201: openapi.Response("Successful response", response_serializer),
            403: openapi.Response("User is blocked", message_serializer),
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Error", message_serializer),
        }
    )
    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def create(self, request, *args, **kwargs):
        """
        Rent out a bike.
        Bike id is provided in body.

        Conditions:
        - User can't be blocked
        - User can't be over renting limit
        - Bike with given id must exist
        - Station where the bike is can't be blocked
        - Bike can't be currently blocked by tech
        - Bike can't be already rented
        - Bike can only be reserved, if reserved by the calling user
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if request.user.state == UserState.blocked:
            return Response(
                {"message": "Blocked users are not allowed to rent bikes."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if request.user.bikes.count() >= request.user.rental_limit:
            return Response(
                {
                    "message": f"User reached rental limit of {request.user.rental_limit}."
                },
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if bike.station.state == StationState.blocked:
            return Response(
                {"message": "Cannot rent a bike from blocked station."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if bike.status == BikeStatus.blocked:
            return Response(
                {"message": "Bike is currently blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if bike.status == BikeStatus.rented:
            return Response(
                {"message": "Bike is currently reserved."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if bike.status == BikeStatus.reserved and bike.reservation.user != request.user:
            return Response(
                {"message": "Bike is currently reserved by different user."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        bike.rent(self.request.user)
        return Response(
            data=ReadBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
        )

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={"bikes": ReadBikeSerializer(self.get_queryset(), many=True).data},
        )


class ReservationsViewSet(
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    serializer_class = ReserveBikeSerializer
    message_serializer = MessageSerializer

    def get_queryset(self):
        return Bike.objects.filter(reservation__user=self.request.user)

    @swagger_auto_schema(
        responses={
            403: openapi.Response("User blocked", message_serializer),
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Errors", message_serializer),
        }
    )
    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def create(self, request, *args, **kwargs):
        """
        Reserve a bike.
        Bike id is provided in body.

        Conditions:
        - User can't be blocked
        - Bike with given id must exist
        - Bike can't be currently be blocked
        - Bike can't be currently be rented
        - Bike can't be already reserved
        - Station where the bike is can't be blocked
        """
        if request.user.state == UserState.blocked:
            return Response(
                {"message": "Blocked users are not allowed to rent bikes."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            bike = Bike.objects.get(id=request.data.get("id"))
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if bike.status != BikeStatus.available:
            return Response(
                {"message": "Bike already blocked, rented or reserved."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if bike.station.state == StationState.blocked:
            return Response(
                {"message": "Station is blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        bike.reserve(self.request.user)
        return Response(
            data=ReserveBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
        )

    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={"bikes": ReserveBikeSerializer(self.get_queryset(), many=True).data},
        )

    @swagger_auto_schema(
        responses={
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Errors", message_serializer),
        }
    )
    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        """
        Cancel bike reservation.

        Conditions:
        - Bike with given id must exist
        - Bike must be currently reserved
        - User cancelling reservation must be the one that reserved the bike
        """
        try:
            reserved_bike = Bike.objects.get(id=kwargs["pk"])
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike does not exist"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if reserved_bike.status != BikeStatus.reserved:
            return Response(
                {"message": "Bike not reserved"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        if reserved_bike.reservation.user != self.request.user:
            return Response(
                {
                    "message": "User cancelling the reservation is not the user that reserved it."
                },
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        reserved_bike.cancel_reservation()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
        )
