from django.contrib import admin

from apps.classes.models import ClassOffering


@admin.register(ClassOffering)
class ClassOfferingAdmin(admin.ModelAdmin):
    list_display = ["name", "weekday", "start_time", "end_time", "room", "instructor_name", "is_active"]
    list_filter = ["weekday", "is_active"]
