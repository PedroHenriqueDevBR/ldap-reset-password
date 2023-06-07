from django.urls import path

from apps.core.views import index, PasswordView


urlpatterns = [
    path("", index, name="index"),
    path("password", PasswordView.as_view(), name="password"),
]
