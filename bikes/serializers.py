from rest_framework import serializers
from rest_framework.fields import SerializerMethodField

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


class RentBikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Bike
        fields = ("station",)


class ReserveBikeSerializer(serializers.ModelSerializer):
    station = StationSerializer()
    reservedAt = SerializerMethodField()
    reservedTill = SerializerMethodField()

    class Meta:
        model = Bike
        fields = ("id", "station", "reservedAt", "reservedTill")

    def get_reservedAt(self, bike):  # noqa
        return bike.reservation.reserved_at

    def get_reservedTill(self, bike):  # noqa
        return bike.reservation.reserved_till
