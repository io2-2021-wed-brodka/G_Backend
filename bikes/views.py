from rest_framework.serializers import ModelSerializer
from rest_framework.viewsets import ModelViewSet

from bikes.models import Bike


class BikeSerializer(ModelSerializer):
    class Meta:
        fields = "__all__"
        model = Bike


class BikeViewSet(ModelViewSet):
    queryset = Bike.objects.all()
    serializer_class = BikeSerializer
