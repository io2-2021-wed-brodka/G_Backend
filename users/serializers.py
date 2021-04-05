from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from users.models import User


class ReadUserSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = User
        fields = ("id", "name")

    @staticmethod
    def get_name(user: User) -> str:
        return user.name
