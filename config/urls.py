"""URL configuration for config project."""

from django.contrib import admin
from django.urls import include, path

from accounts.views import DashboardView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("devices/", include("devices.urls")),
    path("", DashboardView.as_view(), name="dashboard"),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
