from django.contrib import admin
from django.urls import path, include
from apps.core import urls as core_urls

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(core_urls)),
]
