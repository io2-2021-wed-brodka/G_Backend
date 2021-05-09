from django.urls import path, include
from rest_framework.routers import DefaultRouter

from users.views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    UserBlockedViewSet,
    UserListAPIView,
    TechViewSet,
)

router = DefaultRouter()
router.register("users/blocked", UserBlockedViewSet, basename="users-blocked")
router.register("techs", TechViewSet, basename="tech")

urlpatterns = [
    path("register/", RegisterAPIView.as_view(), name="register"),
    path("login/", LoginAPIView.as_view(), name="login"),
    path("logout/", LogoutAPIView.as_view(), name="logout"),
    path("users/", UserListAPIView.as_view(), name="user-list"),
    path("", include(router.urls)),
]
