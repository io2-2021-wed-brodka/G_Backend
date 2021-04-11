from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from stations.models import Station, StationState
from stations.serializers import StationSerializer


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer

    @action(detail=False, methods=["post"])
    def blocked(self, request):
        try:
            station = Station.objects.get(id=request.data.get("id"))
        except Station.DoesNotExist:
            return Response(
                {"message": "station not found"}, status=status.HTTP_404_NOT_FOUND
            )
        if station.state == StationState.working:
            station.state = StationState.blocked
            station.save()
            return Response(
                {"id": f"{station.id}", "name": f"{station.name}"},
                status=status.HTTP_201_CREATED,
            )
        else:
            return Response(
                {"message": "station already blocked"},
                status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
