from django.contrib.auth import authenticate
from django.http import Http404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, mixins
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from drf_yasg import openapi

from core.decorators import restrict
from core.serializers import MessageSerializer, IdSerializer
from users.models import User, UserRole, UserState
from users.serializers import (
    RegisterRequestSerializer,
    LoginRequestSerializer,
    ReadUserSerializer,
    LoginResponseSerializer,
    RegisterResponseSerializer,
    CreateTechSerializer,
)


class RegisterAPIView(APIView):
    permission_classes = (AllowAny,)  # no permissions needed to register
    request_serializer = RegisterRequestSerializer
    response_serializer = RegisterResponseSerializer
    message_serializer = MessageSerializer

    @swagger_auto_schema(
        request_body=request_serializer,
        responses={
            200: openapi.Response("Successful response", response_serializer),
            409: openapi.Response("Errors", message_serializer),
        },
    )
    def post(self, request):
        ser = self.request_serializer(data=request.data)
        if not ser.is_valid():
            return Response(
                status=status.HTTP_409_CONFLICT,
                data=self.message_serializer(
                    data={"message": "Invalid request."}
                ).initial_data,
            )
        if User.objects.filter(username=ser.data["login"]).exists():
            return Response(
                status=status.HTTP_409_CONFLICT,
                data=self.message_serializer(
                    data={"message": "Username already taken."}
                ).initial_data,
            )
        user = User.objects.create_user(
            username=ser.data["login"],
            password=ser.data["password"],
            role=UserRole.user,
        )
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            status=status.HTTP_200_OK,
            data=self.response_serializer({"token": token.key}).data,
        )


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)  # no permissions needed to log in
    request_serializer = LoginRequestSerializer
    response_serializer = LoginResponseSerializer
    message_serializer = MessageSerializer

    @swagger_auto_schema(
        responses={
            200: openapi.Response("Successful response", LoginResponseSerializer),
            401: openapi.Response("Bad credentials", message_serializer),
        }
    )
    def post(self, request, *args, **kwargs):
        # we wrap default DRF obtain_auth_token flow to be compliant with specification
        ser = self.request_serializer(data=request.data)
        if not ser.is_valid():
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data=self.message_serializer(
                    data={"message": "Bad credentials."}
                ).initial_data,
            )
        user = authenticate(
            request=request,
            username=ser.data["login"],
            password=ser.data["password"],
        )
        if not user:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data=self.message_serializer(
                    data={"message": "Bad credentials."}
                ).initial_data,
            )
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            status=status.HTTP_200_OK,
            data=self.response_serializer(
                data={"token": token.key, "role": user.role}
            ).initial_data,
        )


class LogoutAPIView(APIView):
    message_serializer = MessageSerializer

    @swagger_auto_schema(
        responses={
            204: openapi.Response("Successful response", message_serializer),
        }
    )
    @restrict(UserRole.user, UserRole.tech, UserRole.admin)
    def post(self, request, *args, **kwargs):
        Token.objects.get(user=request.user).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data=self.message_serializer(
                data={"message": "Successfully logged out."}
            ).initial_data,
        )


class UserListAPIView(ListAPIView):
    queryset = User.objects.filter(role=UserRole.user)
    serializer_class = ReadUserSerializer

    @restrict(UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={"users": self.serializer_class(self.get_queryset(), many=True).data},
        )


class UserBlockedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = User.objects.filter(role=UserRole.user, state=UserState.blocked)
    request_serializer = IdSerializer
    serializer_class = ReadUserSerializer
    message_serializer = MessageSerializer

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(
                data={"message": "User not blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return super().handle_exception(exc)

    @swagger_auto_schema(
        request_body=request_serializer,
        responses={
            201: openapi.Response("Successful response", serializer_class),
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Errors", message_serializer),
        },
    )
    @restrict(UserRole.admin)
    def create(self, request, *args, **kwargs):
        ser = self.request_serializer(data=request.data)
        if not ser.is_valid():
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={"message": "No id provided."},
            )
        try:
            user = User.objects.get(id=ser.data["id"])
        except User.DoesNotExist:
            return Response(
                status=status.HTTP_404_NOT_FOUND, data={"message": "User not found."}
            )
        if user.state == UserState.blocked:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={"message": "User already blocked."},
            )
        # this one is not in specification, but made sense
        if user.role != UserRole.user:
            return Response(
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
                data={"message": "Can only block users."},
            )
        user.block()
        return Response(
            status=status.HTTP_201_CREATED, data=self.serializer_class(user).data
        )

    @restrict(UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={"users": self.serializer_class(self.get_queryset(), many=True).data},
        )

    @swagger_auto_schema(
        responses={
            204: openapi.Response("Successful response", message_serializer),
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Not blocked", message_serializer),
        }
    )
    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.unblock()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TechViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = User.objects.filter(role=UserRole.tech)
    serializer_class = ReadUserSerializer
    request_serializer = CreateTechSerializer
    response_serializer = RegisterRequestSerializer
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
        ser = self.request_serializer(data=request.data)
        if not ser.is_valid():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data=self.message_serializer(
                    data={"message": "Invalid request."}
                ).initial_data,
            )
        if User.objects.filter(username=ser.data["name"]).exists():
            return Response(
                status=status.HTTP_409_CONFLICT,
                data=self.message_serializer(
                    data={"message": "Username already taken."}
                ).initial_data,
            )
        user = User.objects.create_user(
            username=ser.data["name"],
            password=ser.data["password"],
            role=UserRole.tech,
        )
        return Response(
            status=status.HTTP_201_CREATED,
            data=self.response_serializer(
                data={
                    "id": str(user.id),
                    "name": ser.data["name"],
                }
            ).initial_data,
        )

    @restrict(UserRole.admin)
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @restrict(UserRole.admin)
    def list(self, request, *args, **kwargs):
        return Response(
            status=status.HTTP_200_OK,
            data={"techs": self.serializer_class(self.get_queryset(), many=True).data},
        )

    @swagger_auto_schema(
        responses={
            404: openapi.Response("Not found", message_serializer),
            422: openapi.Response("Not blocked", message_serializer),
        }
    )
    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        try:
            user = User.objects.get(role=UserRole.tech, id=kwargs["pk"])
        except User.DoesNotExist:
            return Response(
                {"message": "Tech does not exist."},
                status=status.HTTP_404_NOT_FOUND,
            )
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
