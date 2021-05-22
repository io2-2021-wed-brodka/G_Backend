from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from stations.models import Station


class StationSerializer(ModelSerializer):
    activeBikesCount = SerializerMethodField()

    class Meta:
        fields = ("id", "name", "state", "activeBikesCount", "capacity")
        model = Station

    @staticmethod
    def get_activeBikesCount(station):  # noqa
        return station.bikes.count()
