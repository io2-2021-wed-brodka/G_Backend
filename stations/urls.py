from django.urls import path, include
from core.routers import OptionalSlashRouter

from stations import views

router = OptionalSlashRouter()
router.register(
    "stations/blocked", views.StationsBlockedViewSet, basename="stations-blocked"
)
router.register("stations", views.StationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
