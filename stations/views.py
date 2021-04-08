from rest_framework.viewsets import ModelViewSet

from stations.models import Station
from stations.serializers import StationSerializer


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
