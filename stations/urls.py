from django.urls import path, include
from rest_framework.routers import DefaultRouter

from stations import views

router = DefaultRouter()
router.register("stations", views.StationViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
