from django.urls import path, re_path, include
from core.routers import OptionalSlashRouter

from users.views import (
    RegisterAPIView,
    LoginAPIView,
    LogoutAPIView,
    UserBlockedViewSet,
    UserListAPIView,
    TechViewSet,
)

router = OptionalSlashRouter()
router.register("users/blocked", UserBlockedViewSet, basename="users-blocked")
router.register("techs", TechViewSet, basename="tech")

urlpatterns = [
    re_path("^register/?$", RegisterAPIView.as_view(), name="register"),
    re_path("^login/?$", LoginAPIView.as_view(), name="login"),
    re_path("^logout/?$", LogoutAPIView.as_view(), name="logout"),
    re_path("^users/?$", UserListAPIView.as_view(), name="user-list"),
    path("", include(router.urls)),
]
