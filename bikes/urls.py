from django.urls import path, include
from core.routers import OptionalSlashRouter

from bikes import views

router = OptionalSlashRouter()
router.register("bikes/rented", views.BikesRentedViewSet, basename="bikes-rented")
router.register("bikes/reserved", views.BikesReservedViewSet, basename="bikes-reserved")
router.register("bikes/blocked", views.BikesBlockedViewSet, basename="bikes-blocked")
router.register("bikes", views.BikeViewSet)
router.register("malfunctions", views.MalfunctionViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
