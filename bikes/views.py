from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import viewsets, status, mixins
from rest_framework.mixins import CreateModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from bikes.models import Bike, BikeStatus, Malfunction

from bikes.serializers import (
    ReadBikeSerializer,
    CreateBikeSerializer,
    RentBikeSerializer,
    ReserveBikeSerializer,
    MalfunctionSerializer,
    CreateMalfunctionSerializer,
)
from core.decorators import restrict
from core.serializers import MessageSerializer, IdSerializer
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
        if not serializer.is_valid():
            return Response(
                {"message": "Id not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        station = serializer.validated_data["station"]
        if station.bikes.count() >= station.bikesLimit:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={
                    "message": "Cannot associate specified bike with specified station, station is full."
                },
            )
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


class BikesRentedViewSet(CreateModelMixin, ListModelMixin, viewsets.GenericViewSet):
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


class BikesReservedViewSet(
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


class BikesBlockedViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Bike.objects.filter(status=BikeStatus.blocked)
    serializer_class = ReadBikeSerializer
    request_serializer = IdSerializer
    message_serializer = MessageSerializer

    @swagger_auto_schema(
        request_body=request_serializer,
        responses={
            201: openapi.Response("Successful response", serializer_class),
            400: openapi.Response("Bad request", message_serializer),
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Not blocked", message_serializer),
        },
    )
    @restrict(UserRole.admin)
    def create(self, request, *args, **kwargs):
        """
        Block a bike.
        Bike id is provided in body.

        Conditions:
        - Bike must exist
        - Bike must be currently working
        """
        ser = self.request_serializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"message": "Id not provided"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            bike = Bike.objects.get(id=ser.data["id"])
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if bike.status != BikeStatus.available:
            return Response(
                {"message": "Bike already blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        bike.block()
        return Response(
            data=self.serializer_class(bike).data,
            status=status.HTTP_201_CREATED,
        )

    @restrict(UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={"bikes": self.serializer_class(self.get_queryset(), many=True).data},
        )

    @swagger_auto_schema(
        responses={
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Not blocked", message_serializer),
        }
    )
    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        """
        Unblock a bike.
        Bike id is provided as part of the url.

        Conditions:
        - Bike must exist
        - Bike must be currently blocked
        """
        try:
            bike = Bike.objects.get(id=kwargs["pk"])
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        if bike.status != BikeStatus.blocked:
            return Response(
                {"message": "Bike not blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        bike.unblock()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MalfunctionViewSet(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Malfunction.objects.all()
    serializer_class = MalfunctionSerializer
    request_serializer = CreateMalfunctionSerializer
    message_serializer = MessageSerializer

    @swagger_auto_schema(
        request_body=request_serializer,
        responses={
            201: openapi.Response("Successful response", serializer_class),
            400: openapi.Response("Bad request", message_serializer),
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Not blocked", message_serializer),
        },
    )
    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def create(self, request, *args, **kwargs):
        """
        Create malfunction report

        Conditions:
        - Bike must exist
        - Bike must be currently rented by reporting user
        """
        ser = self.request_serializer(data=request.data)
        if not ser.is_valid():
            return Response(
                {"message": "Provide bike id and description."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            bike = Bike.objects.get(id=ser.data["id"])
        except Bike.DoesNotExist:
            return Response(
                {"message": "Bike not found."}, status=status.HTTP_404_NOT_FOUND
            )
        if bike.status != BikeStatus.rented or bike.user != request.user:
            return Response(
                {"message": "Bike not rented by reporting user."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        malfunction = Malfunction.objects.create(
            bike=bike, description=ser.data["description"], reporting_user=request.user
        )
        return Response(
            data=self.serializer_class(malfunction).data,
            status=status.HTTP_201_CREATED,
        )

    @restrict(UserRole.tech, UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={
                "malfunctions": self.serializer_class(
                    self.get_queryset(), many=True
                ).data
            },
        )

    @swagger_auto_schema(
        responses={
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Not blocked", message_serializer),
        }
    )
    @restrict(UserRole.tech, UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        """
        Delete malfunction report.
        """
        try:
            malfunction = Malfunction.objects.get(id=kwargs["pk"])
        except Malfunction.DoesNotExist:
            return Response(
                {"message": "Malfunction does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )

        malfunction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
