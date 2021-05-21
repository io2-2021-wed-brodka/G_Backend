from django.urls import path, include
from rest_framework.routers import DefaultRouter

from bikes import views

router = DefaultRouter()
router.register("bikes/rented", views.BikesRentedViewSet, basename="bikes-rented")
router.register("bikes/reserved", views.BikesReservedViewSet, basename="bikes-reserved")
router.register("bikes/blocked", views.BikesBlockedViewSet, basename="bikes-blocked")
router.register("bikes", views.BikeViewSet)
router.register("malfunctions", views.MalfunctionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
