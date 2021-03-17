from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from stations.models import Station


class StationSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Station


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
