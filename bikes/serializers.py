from rest_framework import serializers

from bikes.models import Bike
from stations.models import Station
from stations.serializers import StationSerializer
from users.serializers import ReadUserSerializer


class ReadBikeSerializer(serializers.ModelSerializer):
    station = StationSerializer()
    user = ReadUserSerializer()

    class Meta:
        model = Bike
        fields = ("id", "station", "user", "status")
        depth = 1


class CreateBikeSerializer(serializers.ModelSerializer):
    stationId = serializers.PrimaryKeyRelatedField(
        source="station", queryset=Station.objects.all()
    )

    class Meta:
        model = Bike
        fields = ("stationId",)
