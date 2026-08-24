from django.db import models

from apps.accounts.models import Student
from apps.classes.models import ClassOffering
from apps.packages.models import Package


class CheckIn(models.Model):
    """One attendance record, created when a student scans the fixed
    physical QR at the room and confirms which class they're attending."""

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="checkins")
    class_offering = models.ForeignKey(ClassOffering, on_delete=models.PROTECT)
    package = models.ForeignKey(
        Package, null=True, blank=True, on_delete=models.SET_NULL, related_name="checkins"
    )
    credit_deducted = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Asistencia"
        verbose_name_plural = "Asistencias"
        ordering = ["-checked_in_at"]

    def __str__(self):
        return f"{self.student} -> {self.class_offering} ({self.checked_in_at:%Y-%m-%d %H:%M})"
