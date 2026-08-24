from django.db import models

from apps.accounts.models import Student
from apps.packages.models import Package


class NotificationLog(models.Model):
    TYPE_LOW_CREDIT = "low_credit"
    TYPE_PACKAGE_EXHAUSTED = "package_exhausted"
    TYPE_PACKAGE_EXPIRED = "package_expired"
    TYPE_CHOICES = [
        (TYPE_LOW_CREDIT, "Le queda 1 clase (correo al alumno)"),
        (TYPE_PACKAGE_EXHAUSTED, "Paquete agotado (alerta a recepción)"),
        (TYPE_PACKAGE_EXPIRED, "Paquete/mensualidad vencida (alerta a recepción)"),
    ]

    CHANNEL_EMAIL = "email"
    CHANNEL_INTERNAL = "internal"
    CHANNEL_CHOICES = [
        (CHANNEL_EMAIL, "Correo al alumno"),
        (CHANNEL_INTERNAL, "Alerta interna (recepción)"),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="notifications")
    package = models.ForeignKey(
        Package, null=True, blank=True, on_delete=models.SET_NULL, related_name="notifications"
    )
    notif_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    channel = models.CharField(max_length=10, choices=CHANNEL_CHOICES)
    message = models.TextField(blank=True)
    sent_at = models.DateTimeField(auto_now_add=True)
    # Internal alerts (recepción) get resolved once the student renews/pays.
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(
        "auth.User", null=True, blank=True, on_delete=models.SET_NULL
    )

    class Meta:
        verbose_name = "Notificación / alerta"
        verbose_name_plural = "Notificaciones / alertas"
        ordering = ["-sent_at"]

    def __str__(self):
        return f"{self.get_notif_type_display()} - {self.student} ({self.sent_at:%Y-%m-%d})"

    @property
    def is_pending(self) -> bool:
        return self.channel == self.CHANNEL_INTERNAL and self.resolved_at is None
