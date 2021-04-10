from rest_framework.serializers import ModelSerializer

from stations.models import Station


class StationSerializer(ModelSerializer):
    class Meta:
        fields = ("id", "name")
        model = Station


class StationBlockedSerializer(ModelSerializer):
    class Meta:
        fields = ("id",)
        model = Station
