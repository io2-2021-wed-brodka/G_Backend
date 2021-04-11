from rest_framework import viewsets, status
from rest_framework.generics import ListAPIView
from rest_framework.response import Response

from bikes.models import Bike, BikeStatus
from bikes.serializers import ReadBikeSerializer, CreateBikeSerializer


class BikeViewSet(viewsets.ModelViewSet):
    queryset = Bike.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return CreateBikeSerializer
        else:
            return ReadBikeSerializer

    def create(self, request, *args, **kwargs):
        # we override the whole CreateModelMixin.create, because we need to keep created object
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        bike = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            data=ReadBikeSerializer(bike).data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )


class RentedBikesListAPIView(ListAPIView):
    queryset = Bike.objects.filter(status=BikeStatus.in_service)
    serializer_class = ReadBikeSerializer
