from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from stations.models import Station, StationState
from stations.serializers import StationSerializer, StationBlockedSerializer


class StationViewSet(ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    flag = 0
    def get_serializer_class(self):
        if self.flag == 1:
            return StationBlockedSerializer
        else:
            return StationSerializer

    @action(detail=False, methods=['post'])
    def blocked(self, request):
        self.flag = 1
        serializer = self.get_serializer(data=request.data)
        self.flag = 0
        if serializer.is_valid():
            try:
                station = Station.objects.get(id=serializer.validated_data.get('id')) #to nie działa właśnie
            except Station.DoesNotExist:
                return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
            print(station)
            if station.state == StationState.working:
                station.state = StationState.blocked
                station.save()
                return Response({'id': f'{station.id}', 'name': f'{station.name}'}, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        else:
            return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)







