"""Модуль для описания urls для аутентификации пользователя"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from my_auth.views import UserLogInAPIView, UserLogOutAPIView, UserRegistrationViewSet

app_name = "my_auth"

routers_my_auth = DefaultRouter(trailing_slash=False)
routers_my_auth.register(r"sign-up", UserRegistrationViewSet, basename="sign-up")


urlpatterns = [
    path("", include(routers_my_auth.urls)),
]

urlpatterns += [
    path("sign-in", UserLogInAPIView.as_view(), name="sign-in"),
    path("sign-out", UserLogOutAPIView.as_view(), name="sign-out"),
]
