from rest_framework import serializers
from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer, Serializer

from users.models import User


class ReadUserSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name")

    @staticmethod
    def get_name(user: User) -> str:
        return user.username


class RegisterSerializer(Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass


class LoginSerializer(Serializer):
    login = serializers.CharField(required=True)
    password = serializers.CharField(required=True)

    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass
