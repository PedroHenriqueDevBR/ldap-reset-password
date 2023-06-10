from django.urls import path

from apps.core.views import (
    index,
    PasswordView,
    RequestMailView,
    ConfirmTokenView,
)


urlpatterns = [
    path("", index, name="index"),
    path("password", PasswordView.as_view(), name="password"),
    path("request/mail", RequestMailView.as_view(), name="mail"),
    path("request/token", ConfirmTokenView.as_view(), name="token"),
]
