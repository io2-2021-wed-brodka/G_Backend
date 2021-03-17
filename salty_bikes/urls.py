from django.urls import path, include

urlpatterns = [
    path("", include("bikes.urls")),
    path("", include("stations.urls")),
]
