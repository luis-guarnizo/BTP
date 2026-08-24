from django.urls import path

from apps.attendance import views

urlpatterns = [
    path("checkin/", views.CheckInView.as_view(), name="checkin"),
    path("", views.CheckInListView.as_view(), name="checkin-list"),
]
