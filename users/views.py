from django.contrib.auth import authenticate
from django.http import Http404
from rest_framework import status, mixins
from rest_framework.authtoken.models import Token
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from core.decorators import restrict
from users.models import User, UserRole, UserState
from users.serializers import RegisterSerializer, LoginSerializer, ReadUserSerializer


class RegisterAPIView(APIView):
    # no permissions needed to register
    permission_classes = (AllowAny,)

    @staticmethod
    def post(request):
        ser = RegisterSerializer(data=request.data)
        if ser.is_valid():
            if User.objects.filter(username=ser.data["login"]).exists():
                return Response(
                    status=status.HTTP_409_CONFLICT,
                    data={"message": "username already taken"},
                )
            user = User.objects.create_user(
                username=ser.data["login"],
                password=ser.data["password"],
                role=UserRole.user,
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response(status=status.HTTP_200_OK, data={"token": token.key})
        return Response(
            status=status.HTTP_409_CONFLICT, data={"message": "invalid request"}
        )


class LoginAPIView(APIView):
    # no permissions needed to log in
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        # we wrap default DRF obtain_auth_token flow to be compliant with specification
        ser = LoginSerializer(data=request.data)
        if (
            ser.is_valid()
            # only authenticate if the role is matching
            and User.objects.filter(
                username=ser.data["login"], role=ser.data["role"]
            ).exists()
        ):
            # fall back to default DRF implementation
            user = authenticate(
                request=request,
                username=ser.data["login"],
                password=ser.data["password"],
            )
            if not user:
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={"message": "bad credentials"},
                )
            token, _ = Token.objects.get_or_create(user=user)
            return Response(status=status.HTTP_200_OK, data={"token": token.key})
        # return specification compliant response
        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={"message": "bad credentials"}
        )


class LogoutAPIView(APIView):
    def post(self, request, *args, **kwargs):
        Token.objects.get(user=request.user).delete()
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={"message": "Successfully logged out."},
        )


class UserListAPIView(ListAPIView):
    queryset = User.objects.all()
    serializer_class = ReadUserSerializer

    @restrict(UserRole.admin)
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class UserBlockedViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    GenericViewSet,
):
    queryset = User.objects.filter(state=UserState.blocked)
    serializer_class = ReadUserSerializer

    def handle_exception(self, exc):
        if isinstance(exc, Http404):
            return Response(
                {"message": "User not blocked."},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        return super().handle_exception(exc)

    @restrict(UserRole.admin)
    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.data.get("id"))
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
            status=status.HTTP_201_CREATED, data=ReadUserSerializer(user).data
        )

    @restrict(UserRole.admin)
    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.unblock()
        return Response(status=status.HTTP_204_NO_CONTENT)
