from rest_framework import serializers
from rest_framework.fields import SerializerMethodField, CharField

from bikes.models import Bike, Malfunction
from core.serializers import IOSerializer
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


class MalfunctionSerializer(serializers.ModelSerializer):
    bikeId = CharField(source="bike.id")
    reportingUserId = CharField(source="reporting_user.id")

    class Meta:
        model = Malfunction
        fields = ("id", "bikeId", "description", "reportingUserId")


class CreateMalfunctionSerializer(IOSerializer):
    id = CharField(required=True)
    description = CharField(required=True)
