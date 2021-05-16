from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from core.serializers import IOSerializer
from users.models import User


class ReadUserSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name")

    @staticmethod
    def get_name(user: User) -> str:
        return user.username


class ListUsersSerializer(IOSerializer):
    users = ReadUserSerializer(required=True, many=True)


class RegisterRequestSerializer(IOSerializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class RegisterResponseSerializer(IOSerializer):
    token = serializers.CharField(required=True)


class LoginRequestSerializer(IOSerializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)


class LoginResponseSerializer(IOSerializer):
    token = serializers.CharField(required=True)
    role = serializers.CharField(required=True)


class CreateTechSerializer(IOSerializer):
    name = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
