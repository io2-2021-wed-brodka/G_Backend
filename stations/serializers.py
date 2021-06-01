from rest_framework.fields import SerializerMethodField
from rest_framework.serializers import ModelSerializer

from bikes.models import BikeStatus
from stations.models import Station


class StationSerializer(ModelSerializer):
    activeBikesCount = SerializerMethodField()

    class Meta:
        fields = ("id", "name", "state", "activeBikesCount", "bikesLimit")
        model = Station

    @staticmethod
    def get_activeBikesCount(station):  # noqa
        return station.bikes.filter(status=BikeStatus.available).count()
