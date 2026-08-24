from django.urls import path

from apps.packages import views

urlpatterns = [
    path("types/", views.PackageTypeListView.as_view(), name="package-type-list"),
    path("", views.PackageListCreateView.as_view(), name="package-list"),
]
