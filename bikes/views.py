from rest_framework import viewsets

from bikes.models import Bike
from bikes.serializers import ReadBikeSerializer, CreateBikeSerializer


class BikeViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBikeSerializer
        else:
            return ReadBikeSerializer
