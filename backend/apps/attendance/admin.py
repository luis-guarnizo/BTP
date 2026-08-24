from django.contrib import admin

from apps.attendance.models import CheckIn


@admin.register(CheckIn)
class CheckInAdmin(admin.ModelAdmin):
    list_display = ["student", "class_offering", "checked_in_at", "credit_deducted"]
    list_filter = ["class_offering", "credit_deducted"]
    search_fields = ["student__first_name", "student__last_name", "student__phone"]
    date_hierarchy = "checked_in_at"
