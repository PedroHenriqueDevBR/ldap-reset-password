from django.urls import path

from apps.core.views import (
    index,
    success,
    PasswordView,
    RequestMailView,
    ConfirmTokenView,
    ChangePasswordToken,
)


urlpatterns = [
    path("", index, name="index"),
    path("success", success, name="success"),
    path("password", PasswordView.as_view(), name="password"),
    path("request/mail", RequestMailView.as_view(), name="mail"),
    path("request/token", ConfirmTokenView.as_view(), name="token"),
    path(
        "request/token/password",
        ChangePasswordToken.as_view(),
        name="token_password",
    ),
]
