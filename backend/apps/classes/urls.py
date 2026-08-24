from django.urls import path

from apps.classes import views

urlpatterns = [
    path("today/", views.TodayClassesView.as_view(), name="classes-today"),
    path("", views.ClassOfferingListCreateView.as_view(), name="class-list"),
    path("<int:pk>/", views.ClassOfferingDetailView.as_view(), name="class-detail"),
]
