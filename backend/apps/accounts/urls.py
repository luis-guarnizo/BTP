from django.urls import path

from apps.accounts import views

urlpatterns = [
    path("csrf/", views.CsrfCookieView.as_view(), name="csrf-cookie"),
    path("checkin-login/", views.CheckinLoginView.as_view(), name="checkin-login"),
    path("checkin-logout/", views.CheckinLogoutView.as_view(), name="checkin-logout"),
    path("me/", views.CheckinMeView.as_view(), name="checkin-me"),
    path("staff-login/", views.StaffLoginView.as_view(), name="staff-login"),
    path("staff-logout/", views.StaffLogoutView.as_view(), name="staff-logout"),
    path("staff-me/", views.StaffMeView.as_view(), name="staff-me"),
    path("students/", views.StudentListCreateView.as_view(), name="student-list"),
    path("students/<int:pk>/", views.StudentDetailView.as_view(), name="student-detail"),
]
