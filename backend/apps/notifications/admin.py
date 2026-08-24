from django.contrib import admin
from django.utils import timezone

from apps.notifications.models import NotificationLog


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ["student", "notif_type", "channel", "sent_at", "is_pending"]
    list_filter = ["notif_type", "channel"]
    search_fields = ["student__first_name", "student__last_name", "student__phone"]
    actions = ["mark_resolved"]

    def mark_resolved(self, request, queryset):
        queryset.filter(resolved_at__isnull=True).update(
            resolved_at=timezone.now(), resolved_by=request.user
        )

    mark_resolved.short_description = "Marcar como resuelto (renovó/pagó)"
