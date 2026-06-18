"""URL configuration for config project."""

from django.contrib import admin
from django.urls import include, path

from accounts.views import DashboardView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("devices/", include("devices.urls")),
    path("", DashboardView.as_view(), name="dashboard"),
]
