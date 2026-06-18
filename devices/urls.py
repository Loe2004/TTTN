from django.urls import path

from . import views

app_name = "devices"

urlpatterns = [
    # Devices
    path("", views.DeviceListView.as_view(), name="device_list"),
    path("add/", views.DeviceCreateView.as_view(), name="device_add"),
    path("<int:pk>/", views.DeviceDetailView.as_view(), name="device_detail"),
    path("<int:pk>/edit/", views.DeviceUpdateView.as_view(), name="device_edit"),
    path(
        "<int:pk>/delete/", views.DeviceDeleteView.as_view(), name="device_delete"
    ),
    path("<int:pk>/qr/", views.DeviceQRView.as_view(), name="device_qr"),
    path("bulk-qr/", views.BulkDeviceQRView.as_view(), name="bulk_qr"),
    path(
        "bulk-deactivate/",
        views.DeviceBulkDeactivateView.as_view(),
        name="bulk_deactivate",
    ),
    # Maintenance logs
    path(
        "<int:device_pk>/logs/add/",
        views.MaintenanceLogCreateView.as_view(),
        name="log_add",
    ),
    # Categories
    path("categories/", views.CategoryListView.as_view(), name="category_list"),
    path(
        "categories/add/",
        views.CategoryCreateView.as_view(),
        name="category_add",
    ),
    path(
        "categories/<int:pk>/edit/",
        views.CategoryUpdateView.as_view(),
        name="category_edit",
    ),
    path(
        "categories/<int:pk>/delete/",
        views.CategoryDeleteView.as_view(),
        name="category_delete",
    ),
    path(
        "categories/bulk-deactivate/",
        views.CategoryBulkDeactivateView.as_view(),
        name="category_bulk_deactivate",
    ),
    # Locations
    path("locations/", views.LocationListView.as_view(), name="location_list"),
    path(
        "locations/add/", views.LocationCreateView.as_view(), name="location_add"
    ),
    path(
        "locations/<int:pk>/edit/",
        views.LocationUpdateView.as_view(),
        name="location_edit",
    ),
    path(
        "locations/<int:pk>/delete/",
        views.LocationDeleteView.as_view(),
        name="location_delete",
    ),
    path(
        "locations/bulk-deactivate/",
        views.LocationBulkDeactivateView.as_view(),
        name="location_bulk_deactivate",
    ),
    # QR scanner + resolve API
    path("scan/", views.ScannerView.as_view(), name="scanner"),
    path(
        "api/resolve/<uuid:uuid>/",
        views.DeviceResolveAPIView.as_view(),
        name="device_resolve",
    ),
]
