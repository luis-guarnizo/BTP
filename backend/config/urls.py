from django.contrib import admin
from django.urls import include, path

from config import admin_site  # noqa: F401  (customizes admin.site headers)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/accounts/", include("apps.accounts.urls")),
    path("api/packages/", include("apps.packages.urls")),
    path("api/classes/", include("apps.classes.urls")),
    path("api/attendance/", include("apps.attendance.urls")),
    path("api/reports/", include("apps.reports.urls")),
]
