from django.contrib import admin

from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("bikes.urls")),
    path("", include("stations.urls")),
    path("", include("users.urls")),
]
