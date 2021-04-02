from rest_framework.status import HTTP_200_OK
from rest_framework.viewsets import ModelViewSet

from stations.models import Station
from stations.serializers import StationSerializer


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    def destroy(self, request, *args, **kwargs):
        station = self.get_object()
        response = super().destroy(request, *args, **kwargs)
        # override due to specification
        response.status_code = HTTP_200_OK
        response.data = StationSerializer(station).data
        return response
