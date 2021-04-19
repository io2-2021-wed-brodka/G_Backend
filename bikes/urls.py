from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bikes import views

router = DefaultRouter()
router.register("bikes/rented", views.RentedBikesViewSet, basename="bikes-rented")
router.register("bikes/reserved", views.ReservationsViewSet, basename="bikes-reserved")
router.register("bikes", views.BikeViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
