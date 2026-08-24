from django.urls import path

from apps.reports import views

urlpatterns = [
    path("revenue/", views.RevenueReportView.as_view(), name="report-revenue"),
    path("students/", views.ActiveStudentsReportView.as_view(), name="report-students"),
    path("attendance/", views.AttendanceReportView.as_view(), name="report-attendance"),
    path("alerts/", views.PendingAlertsView.as_view(), name="report-alerts"),
    path("alerts/<int:pk>/resolve/", views.ResolveAlertView.as_view(), name="report-alert-resolve"),
]
