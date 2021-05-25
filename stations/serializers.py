from rest_framework.fields import SerializerMethodField, IntegerField
from rest_framework.serializers import ModelSerializer

from bikes.models import BikeStatus
from stations.models import Station


class StationSerializer(ModelSerializer):
    activeBikesCount = SerializerMethodField()
    bikeLimit = IntegerField(write_only=True)

    class Meta:
        fields = ("id", "name", "state", "activeBikesCount", "bikeLimit")
        model = Station

    @staticmethod
    def get_activeBikesCount(station):  # noqa
        return station.bikes.filter(status=BikeStatus.available).count()

    def create(self, validated_data):
        validated_data["capacity"] = validated_data["bikeLimit"]
        del validated_data["bikeLimit"]
        return super().create(validated_data)
