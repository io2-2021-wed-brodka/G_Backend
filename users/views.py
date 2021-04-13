from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User, UserRole
from users.serializers import RegisterSerializer, LoginSerializer


class RegisterAPIView(APIView):
    @staticmethod
    def post(request):
        ser = RegisterSerializer(data=request.data)
        if (
            ser.is_valid()
            and not User.objects.filter(username=ser.data["username"]).exists()
        ):
            user = User.objects.create_user(
                username=ser.data["username"],
                password=ser.data["password"],
                role=UserRole.user,
            )
            token, _ = Token.objects.get_or_create(user=user)
            return Response(status=status.HTTP_200_OK, data={"token": token.key})
        return Response(
            status=status.HTTP_409_CONFLICT, data={"message": "username already taken"}
        )


class LoginAPIView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        # we wrap default DRF obtain_auth_token flow to be compliant with specification
        ser = LoginSerializer(data=request.data)
        if (
            ser.is_valid()
            # only authenticate if the role is matching
            and User.objects.filter(
                username=ser.data["username"], role=ser.data["role"]
            ).exists()
        ):
            try:
                # fall back to default DRF implementation
                return super().post(request, *args, **kwargs)
            except ValidationError:
                # return specification compliant response
                return Response(
                    status=status.HTTP_401_UNAUTHORIZED,
                    data={"message": "bad credentials"},
                )
        # return specification compliant response
        return Response(
            status=status.HTTP_401_UNAUTHORIZED, data={"message": "bad credentials"}
        )
