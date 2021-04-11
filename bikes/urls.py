from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bikes import views

router = DefaultRouter()
router.register("bikes", views.BikeViewSet)

urlpatterns = [
    path(
        "bikes/rented/", views.RentedBikesListAPIView.as_view(), name="rented-bike-list"
    ),
    path("", include(router.urls)),
]
