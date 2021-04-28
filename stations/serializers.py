from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from stations.models import Station


class StationSerializer(ModelSerializer):
    activeBikesCount = SerializerMethodField()

    class Meta:
        fields = ("id", "name", "state", "activeBikesCount")
        model = Station

    def get_activeBikesCount(self, station):
        return station.bikes.count()
