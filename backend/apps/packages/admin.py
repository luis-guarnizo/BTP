from django.contrib import admin

from apps.packages.models import Package, PackageType


@admin.register(PackageType)
class PackageTypeAdmin(admin.ModelAdmin):
    list_display = ["name", "category", "price", "credit_count", "is_active"]
    list_filter = ["category", "is_active"]


@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = [
        "student",
        "package_type",
        "purchase_date",
        "expires_at",
        "credits_remaining",
        "status",
        "payment_method",
    ]
    list_filter = ["package_type__category", "payment_method"]
    search_fields = ["student__first_name", "student__last_name", "student__phone"]
    autocomplete_fields = ["student"]

    def status(self, obj):
        return obj.status

    status.short_description = "Estado"
