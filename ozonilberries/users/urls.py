"""Модуль для описания urls для модели 'Profile'"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import ProfileAPIView, ProfileViewSet

app_name = "users"

routers_users = DefaultRouter()
routers_users.register(r"profile", ProfileViewSet, basename="profile")

urlpatterns = [
    path("", include(routers_users.urls)),
]

urlpatterns += [
    path("profile", ProfileAPIView.as_view(), name="profile"),
]
