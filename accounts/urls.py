from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("login/", views.LoginView.as_view(), name="login"),
    path("register/", views.RegisterView.as_view(), name="register"),
    path("logout/", views.LogoutView.as_view(), name="logout"),
    path("register/status/", views.RegisterStatusView.as_view(), name="register_status"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    path(
        "password/change/",
        views.PasswordChangeView.as_view(),
        name="password_change",
    ),
    # Forgot password flow
    path(
        "password/reset/",
        views.PasswordResetView.as_view(),
        name="password_reset",
    ),
    path(
        "password/reset/done/",
        views.PasswordResetDoneView.as_view(),
        name="password_reset_done",
    ),
    path(
        "password/reset/confirm/<uidb64>/<token>/",
        views.PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "password/reset/complete/",
        views.PasswordResetCompleteView.as_view(),
        name="password_reset_complete",
    ),
    # User management (Admin only)
    path("admin-dashboard/", views.AdminDashboardView.as_view(), name="admin_dashboard"),
    path("users/", views.UserListView.as_view(), name="user_list"),
    path("users/pending/", views.PendingUserListView.as_view(), name="user_pending_list"),
    path("users/<int:pk>/approve/", views.ApproveUserView.as_view(), name="user_approve"),
    path("users/<int:pk>/reject/", views.RejectUserView.as_view(), name="user_reject"),
    path("users/<int:pk>/action/", views.UserActionView.as_view(), name="user_action"),
    path("users/add/", views.UserCreateView.as_view(), name="user_add"),
    path("users/<int:pk>/edit/", views.UserUpdateView.as_view(), name="user_edit"),
    path(
        "users/<int:pk>/delete/",
        views.UserDeleteView.as_view(),
        name="user_delete",
    ),
    path(
        "users/<int:pk>/hard-delete/",
        views.UserHardDeleteView.as_view(),
        name="user_hard_delete",
    ),
    path(
        "users/bulk-deactivate/",
        views.UserBulkDeactivateView.as_view(),
        name="user_bulk_deactivate",
    ),
    path(
        "users/<int:pk>/unlock/",
        views.UserUnlockView.as_view(),
        name="user_unlock",
    ),
    path(
        "users/bulk-activate/",
        views.UserBulkActivateView.as_view(),
        name="user_bulk_activate",
    ),
]
